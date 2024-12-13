#!/usr/bin/env python3

import os
import google.generativeai as genai
import subprocess
import json

# Configuração da API key
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY environment variable not set.")
    exit(1)

genai.configure(api_key=api_key)

# Configuração do modelo
try:
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config={
            "temperature": 0.1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
    )
except Exception as e:
    print(f"Error initializing GenerativeModel: {e}")
    exit(1)

# Comandos permitidos
ALLOWED_COMMANDS = [
    "ls", "cd", "pwd", "cp", "mv", "rm", "mkdir", "find", "grep", "df", "du", "tree",
    "touch", "cat", "echo", "head", "tail", "chmod", "chown", "tar", "zip", "unzip", "wget",
    "curl", "nano", "vim", "ps", "kill", "top", "htop", "sudo", "whoami", "uptime", "man",
    "history", "alias", "uname", "mount", "umount"
]

def execute_command(command, flags=None, args=None, requires_sudo=False):
    """Executa comandos Linux com validação."""
    if command not in ALLOWED_COMMANDS:
        return f"Error: Command '{command}' is not allowed."

    # Tratar o comando history separadamente
    if command == "history":
        try:
            # Tenta ler o histórico do arquivo padrão do bash
            history_file = os.path.expanduser("~/.bash_history")
            with open(history_file, "r") as f:
                history_content = f.readlines()
            return ''.join(history_content[-20:])  # Retorna as últimas 20 entradas
        except FileNotFoundError:
            return "Error: Bash history file not found."
        except Exception as e:
            return f"Error accessing history: {str(e)}"

    full_command = [command]
    if flags:
        full_command.extend(flags)
    if args:
        full_command.extend(args)

    try:
        if requires_sudo:
            full_command = ["sudo"] + full_command
        result = subprocess.run(full_command, capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        return output if output else "Comando executado com sucesso (sem saída)"
    except subprocess.CalledProcessError as e:
        return f"Error executing command: {e.stderr.strip()}"
    except Exception as e:
        return f"Error: {str(e)}"

# Configuração do chat
SYSTEM_PROMPT = """Você é um assistente Linux especializado em ajudar com comandos do terminal.
Você DEVE usar a função execute_command para executar comandos.
Regras importantes:
1. Quando o usuário pedir para listar ou usar ls, você DEVE executar o comando ls com os argumentos apropriados
2. Se o usuário não especificar o caminho, use o diretório atual (.)
3. Para comandos de navegação como cd Desktop, use /home/rp/Desktop
4. Sempre use o caminho completo quando mencionado Desktop ou Documents
5. Não explique comandos, apenas execute-os
6. No comando ls, use -la quando quiser mostrar detalhes
"""

try:
    chat = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [SYSTEM_PROMPT]
            },
            {
                "role": "model", 
                "parts": ["Entendido. Vou executar os comandos diretamente usando execute_command."]
            }
        ]
    )
except Exception as e:
    print(f"Error initializing chat: {e}")
    exit(1)

def process_input(user_input):
    try:
        function_declarations = [{
            "name": "execute_command",
            "description": "Executa comandos Linux",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Nome do comando Linux",
                        "enum": ALLOWED_COMMANDS
                    },
                    "flags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Flags do comando (ex: -l, -a)"
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Argumentos do comando como paths ou padrões"
                    },
                    "requires_sudo": {
                        "type": "boolean",
                        "description": "Se precisa de sudo"
                    }
                },
                "required": ["command"]
            }
        }]

        response = chat.send_message(
            content=user_input,
            tools=[{
                "function_declarations": function_declarations
            }]
        )

        for candidate in response.candidates:
            for part in candidate.content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    function_args = part.function_call.args
                    args_dict = dict(function_args)
                    
                    # Converter flags e args para listas se existirem
                    if 'flags' in args_dict:
                        args_dict['flags'] = list(args_dict['flags'])
                    if 'args' in args_dict:
                        args_dict['args'] = list(args_dict['args'])
                    
                    return execute_command(**args_dict)
                elif hasattr(part, 'text'):
                    return part.text

        return "Não entendi o comando."

    except Exception as e:
        print(f"Debug - Error type: {type(e)}")
        print(f"Debug - Error details: {str(e)}")
        return f"Erro ao processar entrada: {str(e)}"

def main():
    print("Assistente Linux iniciado. Digite 'exit' para sair.")
    while True:
        user_input = input("> ").strip()
        
        if user_input.lower() == "exit":
            print("Encerrando assistente...")
            break
            
        if user_input:
            output = process_input(user_input)
            print(output)

if __name__ == "__main__":
    main()
