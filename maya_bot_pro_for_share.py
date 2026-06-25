# -*- coding: utf-8 -*-
import sys
import json
import re
import os
import time
import maya.cmds as cmds

# =========================================================================
# 1. CROSS-VERSION UI COMPATIBILITY (Maya 2020 - 2025)
# =========================================================================
try:
    # For Maya 2025 and newer
    from PySide6 import QtWidgets, QtCore, QtGui
    Signal = QtCore.Signal
except ImportError:
    try:
        # For Maya 2020 - 2024
        from PySide2 import QtWidgets, QtCore, QtGui
        Signal = QtCore.Signal
    except ImportError:
        from PyQt5 import QtWidgets, QtCore, QtGui
        Signal = QtCore.pyqtSignal

# Network connection support across versions (Python 2 and 3)
if sys.version_info[0] < 3:
    import urllib2 as urllib_request
else:
    import urllib.request as urllib_request

# =========================================================================
# 2. DYNAMIC API & TIGHTENED RULES (Token Optimization)
# =========================================================================
def get_gemini_response(prompt_text):
    # =====================================================================
    # [ACTION REQUIRED]: Put your Gemini API Key here
    # =====================================================================
    API_KEY =  "YOUR_GEMINI_API_KEY_HERE"
    
    if API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        return "Error: Please set your Gemini API key in the script."

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key=" + API_KEY
    
    # Automatically check Maya version
    maya_ver = cmds.about(version=True)
    is_python3 = sys.version_info[0] >= 3
    
    # Create Base System Prompt
    system_instruction = "You are an elite Maya TD Developer. Target: Maya " + maya_ver + ".\n"
    if is_python3:
        system_instruction += "RULE: STRICTLY use Python 3 syntax. You can use f-strings.\n"
        ui_module = "PySide6" if "2025" in maya_ver else "PySide2"
        system_instruction += "RULE: For UI, ALWAYS use " + ui_module + ".\n"
    else:
        system_instruction += "RULE: STRICTLY use Python 2.7 syntax. No f-strings.\n"
        system_instruction += "RULE: For UI, ALWAYS use PySide2.\n"

    # Base Operational Rules
    system_instruction += """
MODE GUIDELINES:
- If prompt has [Mode: Quick Action]: Return ONLY raw python code, no def, no docstring, executed immediately.
- If prompt has [Mode: Save Script]: Write formal tool code. CRITICAL RULE: You MUST call the main function or instantiate the UI at the very end of the script outside of comments. NEVER leave the execution command as an example in comments.
Parent UI using: `maya_main_window = {obj.objectName(): obj for obj in QtWidgets.QApplication.topLevelWidgets()}.get('MayaWindow')`
"""
    # Context-Aware Injection (Tightened Rules)
    prompt_lower = prompt_text.lower()
    
    # TIGHTENED ARNOLD RULES: Prevent rendering crashes and deprecated attributes
    if any(kw in prompt_lower for kw in ['render', 'arnold', 'light', 'เรนเดอร์', 'แสง', 'material']):
        system_instruction += """
ARNOLD STRICT RULES:
1. Load 'mtoa' plugin. Use 'asShader=True' for materials, 'asLight=True' for lights.
2. NEVER use cmds.hyperShade. ALWAYS assign materials using a Shading Group (cmds.sets).
3. NEVER use .specularWeight (use strictly .specular for shininess).
4. NEVER write cmds.arnoldRender() in the script (leave rendering to the user).
"""
        
    # TIGHTENED RIGGING RULES
    if any(kw in prompt_lower for kw in ['rig', 'joint', 'skin', 'weight', 'กระดูก']):
        system_instruction += "\nRIGGING RULES: Maintain clean hierarchy. Use proper suffixes (_jnt, _ctrl, _grp). Use cmds.joint(), cmds.skinCluster(). Avoid hardcoding names."

    data = {
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {"temperature": 0.2}
    }
    
    json_data = json.dumps(data).encode('utf-8') if is_python3 else json.dumps(data)
    req = urllib_request.Request(url, data=json_data, headers={'Content-Type': 'application/json'})
    
    try:
        response = urllib_request.urlopen(req)
        raw_res = response.read()
        result = json.loads(raw_res.decode('utf-8') if is_python3 else raw_res)
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return "API Error: " + str(e)

# =========================================================================
# 3. BACKGROUND WORKER THREAD
# =========================================================================
class AIWorker(QtCore.QThread):
    finished_signal = Signal(str)
    def __init__(self, prompt_text, parent=None):
        super(AIWorker, self).__init__(parent)
        self.prompt_text = prompt_text
    def run(self):
        response = get_gemini_response(self.prompt_text)
        self.finished_signal.emit(response)

# =========================================================================
# 4. MAIN UI WORKSPACE
# =========================================================================
class MayaAIBotWorkspace(QtWidgets.QDialog):
    def __init__(self, parent=None):
        maya_main_window = {obj.objectName(): obj for obj in QtWidgets.QApplication.topLevelWidgets()}.get('MayaWindow')
        super(MayaAIBotWorkspace, self).__init__(parent=maya_main_window)
        
        maya_ver = cmds.about(version=True)
        self.setWindowTitle("Maya TD Bot (Ultimate Pro - Maya {})".format(maya_ver))
        self.setWindowFlags(QtCore.Qt.Window) 
        self.resize(550, 600)
        self.worker = None 
        
        main_layout = QtWidgets.QVBoxLayout(self)
        
        # --- Quick Tools Bar ---
        tools_layout = QtWidgets.QHBoxLayout()
        
        self.btn_vscode = QtWidgets.QPushButton("Open VS Code Port (7001)")
        self.btn_vscode.setStyleSheet("background-color: #007ACC; color: white; padding: 4px; font-weight: bold;")
        self.btn_vscode.clicked.connect(self.open_vscode_port)
        
        self.btn_save = QtWidgets.QPushButton("Quick Save Scene")
        self.btn_save.setStyleSheet("background-color: #2E8B57; color: white; padding: 4px; font-weight: bold;")
        self.btn_save.clicked.connect(self.quick_save_scene)

        tools_layout.addWidget(self.btn_vscode)
        tools_layout.addWidget(self.btn_save)
        tools_layout.addStretch()
        main_layout.addLayout(tools_layout)

        # --- Chat History Section ---
        self.chat_history = QtWidgets.QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("background-color: #1E1E1E; color: #D4D4D4; font-family: 'Consolas', 'Courier New'; font-size: 11pt;")
        main_layout.addWidget(self.chat_history)
        
        # --- Input Section ---
        input_layout = QtWidgets.QHBoxLayout()
        self.input_line = QtWidgets.QLineEdit()
        self.input_line.setPlaceholderText("Command the AI (Type 'script' / 'สคริป' to save tool)...")
        self.input_line.setStyleSheet("background-color: #2D2D30; color: #FFFFFF; padding: 6px; font-size: 10pt;")
        self.input_line.returnPressed.connect(self.execute_submit)
        
        self.send_button = QtWidgets.QPushButton("Send")
        self.send_button.setMinimumHeight(32)
        self.send_button.setStyleSheet("background-color: #444444; color: #FFFFFF; font-weight: bold;")
        self.send_button.clicked.connect(self.execute_submit)
        
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.send_button)
        main_layout.addLayout(input_layout)
        
        self.chat_history.append("<b style='color:#4CAF50;'>[System]:</b> Ready. Maya Version: {}<br>".format(maya_ver))

    def execute_submit(self):
        user_text = self.input_line.text().strip()
        if not user_text: return
        
        text_lower = user_text.lower()
        
        # [FIX]: Safe Unicode decoding for Thai language in Python 2
        is_python2 = sys.version_info[0] < 3
        if is_python2:
            keyword_th = "สคริป".decode('utf-8')
            if isinstance(user_text, unicode):
                safe_user_text = user_text.encode('utf-8')
            else:
                safe_user_text = user_text
        else:
            keyword_th = "สคริป"
            safe_user_text = user_text

        # Mode Selection
        if "script" in text_lower or keyword_th in text_lower:
            self.current_mode = "script"
            mode_display = "<span style='color:#FFC107;'>[Mode: Save Script]</span>"
            prompt_modifier = " [Mode: Save Script]"
        else:
            self.current_mode = "action"
            mode_display = "<span style='color:#00BCD4;'>[Mode: Quick Action]</span>"
            prompt_modifier = " [Mode: Quick Action]"

        self.chat_history.append("<b style='color:#64B5F6;'>You:</b> {} {}".format(safe_user_text, mode_display))
        self.chat_history.append("<i><span style='color:#808080;'>Gemini is thinking...</span></i>")
        self.input_line.clear()
        
        self.send_button.setEnabled(False)
        self.input_line.setEnabled(False)
        self.chat_history.verticalScrollBar().setValue(self.chat_history.verticalScrollBar().maximum())
        
        self.worker = AIWorker(safe_user_text + prompt_modifier)
        self.worker.finished_signal.connect(self.process_ai_response)
        self.worker.start()

    def process_ai_response(self, ai_response):
        self.chat_history.append("<b style='color:#E040FB;'>AI TD Bot:</b><br>" + ai_response.replace('\n', '<br>') + "<br>")
        
        # Regex to extract code blocks
        code_blocks = re.findall(r'```python\n(.*?)\n```', ai_response, re.DOTALL)
        if not code_blocks: code_blocks = re.findall(r'```(.*?)\n```', ai_response, re.DOTALL)
        if not code_blocks: code_blocks = re.findall(r'```(.*?)```', ai_response, re.DOTALL)
        
        if code_blocks:
            code_to_run = code_blocks[0].strip()
            if code_to_run.startswith('python'): code_to_run = code_to_run[6:].strip()
            
            if hasattr(self, 'current_mode') and self.current_mode == "script":
                # SAVE SCRIPT MODE
                user_app_dir = cmds.internalVar(userAppDir=True)
                script_dir = os.path.join(user_app_dir, cmds.about(version=True), "scripts")
                if not os.path.exists(script_dir): os.makedirs(script_dir)
                full_path = os.path.join(script_dir, "ai_script_{}.py".format(int(time.time())))
                try:
                    with open(full_path, "w") as f:
                        f.write(code_to_run.encode('utf-8') if sys.version_info[0] < 3 else code_to_run)
                    self.chat_history.append("<br><b style='color:#FFC107;'>[System]: Tool saved! Ready for VS Code.</b>")
                    self.chat_history.append("Path: <a href='#' style='color:#ffff88;'>{}</a><br>".format(full_path))
                    cmds.evalDeferred('import maya.cmds as cmds; cmds.rehash()')
                except Exception as e:
                    self.chat_history.append("<br><b style='color:#F44336;'>[Save Error]: {}</b><br>".format(str(e)))
            else:
                # QUICK ACTION MODE
                self.chat_history.append("<i><span style='color:#808080;'>Executing action in memory...</span></i>")
                QtWidgets.QApplication.processEvents()
                try:
                    exec(code_to_run, globals())
                    self.chat_history.append("<br><b style='color:#00BCD4;'>[System]: Action Successful!</b><br>")
                except Exception as e:
                    self.chat_history.append("<br><b style='color:#F44336;'>[Execute Error]: {}</b><br>".format(str(e)))
                    
        self.chat_history.verticalScrollBar().setValue(self.chat_history.verticalScrollBar().maximum())
        self.send_button.setEnabled(True)
        self.input_line.setEnabled(True)
        self.input_line.setFocus()

    # =====================================================================
    # QUICK TOOLS COMMANDS
    # =====================================================================
    def open_vscode_port(self):
        port_name = ":7001"
        if not cmds.commandPort(port_name, query=True):
            cmds.commandPort(name=port_name)
            self.chat_history.append("<b style='color:#007ACC;'>[System]: Command Port 7001 Opened! Ready for VS Code (Alt+Enter).</b><br>")
        else:
            self.chat_history.append("<b style='color:#007ACC;'>[System]: Port 7001 is already open.</b><br>")

    def quick_save_scene(self):
        try:
            scene_name = cmds.file(query=True, sceneName=True)
            if not scene_name:
                self.chat_history.append("<b style='color:#F44336;'>[Warning]: Scene has no name. Please 'Save As' manually first.</b><br>")
            else:
                cmds.file(save=True)
                self.chat_history.append("<b style='color:#2E8B57;'>[System]: Scene saved successfully!</b><br>")
        except Exception as e:
            self.chat_history.append("<b style='color:#F44336;'>[Error]: {}</b><br>".format(str(e)))

# =========================================================================
# RUN WINDOW
# =========================================================================
try:
    global_maya_ai_window.close()
    global_maya_ai_window.deleteLater()
except NameError:
    pass

global_maya_ai_window = MayaAIBotWorkspace()
global_maya_ai_window.show()