[https://youtu.be/_uS4oIFnTaQ](https://youtu.be/_uS4oIFnTaQ)

# Maya TD Bot 🚀🐍

Transitioning from Rotomation to Programming over the past year has been an incredible journey. **The Maya TD Bot** is a personal project I’ve been developing to bridge the gap between AI and 3D pipelines. 

As someone who works closely with Autodesk Maya, I wanted an AI assistant that doesn’t just generate generic Python scripts, but actually understands the strict constraints of a production environment. I built this tool using the Gemini API, focusing on making it a practical, production-ready assistant.

## ✨ Technical Highlights

🔹 **Cross-Version UI Compatibility:** Dynamically handles PySide2 and PySide6, ensuring the tool works seamlessly from Maya 2020 all the way to 2025.
🔹 **Context-Aware Injection & Guardrails:** I implemented strict token rules. For example, the bot is restricted from using `cmds.hyperShade` or hardcoding joint names, ensuring it strictly follows clean Rigging and Arnold rendering standards.
🔹 **Dual Execution Modes:**
  * **[Quick Action]:** For executing direct commands in memory without cluttering the script editor.
  * **[Save Script]:** For generating formal tools, which it automatically saves to the Maya scripts directory and opens a command port (7001) ready for VS Code debugging.
🔹 **Background Threading:** Utilizing `QThread` so Maya's UI doesn't freeze while waiting for the API response.

## ⚠️ Prerequisites

To use this tool, you will need a valid **Gemini API Key**. You can obtain one for free from [Google AI Studio](https://aistudio.google.com/).

## ⚙️ Setup & Installation

1. Download or clone this repository.
2. Open the main script file (e.g., `maya_bot_pro.py`).
3. Locate the `API_KEY` variable inside the script.
4. Replace `"YOUR_GEMINI_API_KEY_HERE"`( at the line number 38 ) with your actual API key.
5. Run the script inside the Autodesk Maya Script Editor.

---
*Created by a developer passionate about 3D Pipeline Automation.*


