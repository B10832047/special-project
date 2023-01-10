import os, subprocess
from flask_socketio import SocketIO, emit
import time

class Detector:
    def add_module(file_name):
        # input: 使用者上傳的檔案名稱
        # 將 module 資訊加入資料庫(包含檔案位址)
        return
    def get_score(module_id, binary_address, socketio):
        # input: 要測試的模型 ID
        # output: 檢測結果(accuracy, loss ...)
        
        # create new env
        print("環境建置中......")
        print(binary_address)
        env_name = "env" + str(module_id)
        print("1")
        activate_env = ". $CONDA_PREFIX/etc/profile.d/conda.sh && conda activate " + env_name
        print("2")
        os.system("conda create --name " + env_name + " python=3.8.3 -y")
        print("3")
        #os.system(activate_env + " && python3 -m pip install pipreqs")
        #os.system(activate_env + " && pipreqs ./ --encoding=utf8")
        
        os.system(activate_env + " && python -m pip install --no-cache-dir -r detector/modules/current_modules/module_" + str(module_id) + "/requirements.txt")
        # testing
        print("模型預測中......")
        binary_address = str(binary_address)
        benign_files = subprocess.check_output("ls " + binary_address + "/benign", shell=True)
        malware_files = subprocess.check_output("ls " + binary_address + "/malware", shell=True)
        benign_files = str(benign_files)[2:-1].split('\\n')[:-1]
        malware_files = str(malware_files)[2:-1].split('\\n')[:-1]
        
        results = []
        benign_results = []
        malware_results = []
        counter = 0
        start_time = time.time()
        TP = 0
        TN = 0
        FP = 0
        FN = 0
        print("start training benign")
        for benign in benign_files:
            msg = 'testing ' + str(counter) + '/' + str(len(benign_files) + len(malware_files))
            socketio.emit('status_response', {'data': msg})
            print("before result")
            result = int(subprocess.check_output(activate_env + "&& python3 detector/modules/current_modules/module_" + str(module_id) + "/main.py -i " + binary_address + "/benign/" + benign, shell=True))
            if result < 2:
                results += [1 - result]
                if result == 0:
                    TN += 1
                else:
                    FP += 1
            benign_results += [result]
            counter += 1
        for malware in malware_files:
            msg = 'testing ' + str(counter) + '/' + str(len(benign_files) + len(malware_files))
            socketio.emit('status_response', {'data': msg})
            result = int(subprocess.check_output(activate_env + "&& python3 detector/modules/current_modules/module_" + str(module_id) + "/main.py -i " + binary_address + "/malware/" + malware, shell=True))
            if result < 2: 
                results += [result]
                if result == 0:
                    FN += 1
                else:
                    TP += 1
            malware_results += [result]
            counter += 1
        run_time = (time.time() - start_time) / 60.0
        print("結果分析中......")
        print(benign_results)
        print(malware_results)
        print("acc:", float(TP + TN)/(TP + FP + FN + TN))
        analyze_result = {"TP":TP, "TN":TN, "FP":FP, "FN":FN, "runtime":run_time}
        print(analyze_result)
     #   accuracy = sum(results) / len(results)
        return analyze_result
