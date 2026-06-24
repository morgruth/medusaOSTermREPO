#!/usr/bin/env python3

import os
import subprocess
import http.server
import socketserver
import threading

# Configured to your exact folder structure
WORKSPACE = r"E:\javascript"
MEDUSA_OS = WORKSPACE
FRONTEND_DIR = os.path.join(MEDUSA_OS, "fs", "src") # Resolves to E:\javascript\medusaOS\fs\src
PORT = 8000

# Portable Toolchains
JAVA_BIN = r"E:\javascript\jdk-25_windows-x64_bin\jdk-25.0.1\bin"
GRADLE_BIN = r"E:\javascript\gradle-9.1.0-bin\gradle-9.1.0\bin"
NODE_BIN = r"E:\javascript\node-v24.18.0-win-x64" # Added your portable Node path

shell_env = os.environ.copy()

# Injected Node, Java, and Gradle into the execution path
shell_env["PATH"] = (
    JAVA_BIN + os.pathsep +
    GRADLE_BIN + os.pathsep +
    NODE_BIN + os.pathsep +
    shell_env.get("PATH", "")
)

shell_env["JAVA_HOME"] = os.path.dirname(JAVA_BIN)
shell_env["GRADLE_HOME"] = os.path.dirname(GRADLE_BIN)

os.chdir(WORKSPACE)


def is_safe_path(path):
    full_path = os.path.abspath(path)
    workspace = os.path.abspath(WORKSPACE)
    return full_path.startswith(workspace)


def start_http_server():
    """Starts a background HTTP web server for the MedusaOS Desktop Environment UI."""
    if not os.path.exists(FRONTEND_DIR):
        os.makedirs(FRONTEND_DIR, exist_ok=True)
        
    class SafeHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def server_thread():
        socketserver.TCPServer.allow_reuse_address = True
        try:
            with socketserver.TCPServer(("", PORT), SafeHandler) as httpd:
                httpd.serve_forever()
        except Exception as e:
            print(f"\n[Server Error] Failed to keep HTTP server alive: {e}")

    srv_thread = threading.Thread(target=server_thread, daemon=True)
    srv_thread.start()


def startup_check():
    print("Restricted Shell")
    print(f"Workspace  : {WORKSPACE}")
    print(f"Java Bin   : {JAVA_BIN}")
    print(f"Gradle Bin : {GRADLE_BIN}")
    print(f"Node Bin   : {NODE_BIN}") # Added to startup display
    print(f"UI Server  : http://localhost:{PORT} -> {FRONTEND_DIR}")
    print()

    try:
        subprocess.run(
            "java -version",
            shell=True,
            env=shell_env
        )
    except Exception:
        print("Java not found")

    try:
        subprocess.run(
            "gradle -v",
            shell=True,
            env=shell_env
        )
    except Exception:
        print("Gradle not found")

    # Added active Node verification check on startup
    try:
        print("\nNode.js Version:")
        subprocess.run(
            "node -v",
            shell=True,
            env=shell_env
        )
    except Exception:
        print("Node.js not found")

    print()
    print("Commands:")
    print("  ls")
    print("  cd <dir>")
    print("  cat <file>")
    print("  setup-medusa")
    print("  exit")
    print()
    print("External commands:")
    print("  java")
    print("  javac")
    print("  gradle")
    print("  gradlew")
    print("  node")
    print("  npm")
    print("  python")
    print("  git")
    print()


def setup_medusa():
    os.makedirs(
        os.path.join(
            MEDUSA_OS,
            "src",
            "main",
            "java",
            "com",
            "example"
        ),
        exist_ok=True
    )

    os.makedirs(
        os.path.join(
            MEDUSA_OS,
            "src",
            "main",
            "kotlin",
            "com",
            "example"
        ),
        exist_ok=True
    )

    build_gradle = """plugins {
    id 'application'
    id 'org.jetbrains.kotlin.jvm' version '2.4.0'
}

repositories {
    mainCentral()
}

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(25)
    }
}

application {
    mainClass = 'com.example.App'
}
"""

    settings_gradle = """rootProject.name = 'medusaOS'
"""

    app_java = """package com.example;

public class App {
    public static void main(String[] args) {
        System.out.println(Utils.INSTANCE.greeting());
        System.out.println("Hello from MedusaOS!");
    }
}
"""

    utils_kt = """package com.example

object Utils {
    fun greeting(): String {
        return "Hello from Kotlin 2.4.0!"
    }
}
"""

    with open(
        os.path.join(MEDUSA_OS, "build.gradle"),
        "w",
        encoding="utf-8"
    ) as f:
        f.write(build_gradle)

    with open(
        os.path.join(MEDUSA_OS, "settings.gradle"),
        "w",
        encoding="utf-8"
    ) as f:
        f.write(settings_gradle)

    with open(
        os.path.join(
            MEDUSA_OS,
            "src",
            "main",
            "java",
            "com",
            "example",
            "App.java"
        ),
        "w",
        encoding="utf-8"
    ) as f:
        f.write(app_java)

    with open(
        os.path.join(
            MEDUSA_OS,
            "src",
            "main",
            "kotlin",
            "com",
            "example",
            "Utils.kt"
        ),
        "w",
        encoding="utf-8"
    ) as f:
        f.write(utils_kt)

    print()
    print("medusaOS project created:")
    print(MEDUSA_OS)
    print()
    print("Next steps:")
    print("gradle wrapper --gradle-version 9.1.0")
    print("gradlew build")
    print("gradlew run")
    print()


def shell():
    start_http_server()
    startup_check()

    while True:
        try:
            cmd = input("> ").strip()

            if not cmd:
                continue

            if cmd == "exit":
                break

            elif cmd == "setup-medusa":
                setup_medusa()

            elif cmd == "ls":
                for item in os.listdir():
                    print(item)

            elif cmd.startswith("cd "):
                target = os.path.abspath(cmd[3:].strip())

                if is_safe_path(target) and os.path.isdir(target):
                    os.chdir(target)
                    print(os.getcwd())
                else:
                    print("Access denied.")

            elif cmd.startswith("cat "):
                file_path = os.path.abspath(cmd[4:].strip())

                if is_safe_path(file_path) and os.path.isfile(file_path):
                    with open(
                        file_path,
                        "r",
                        encoding="utf-8"
                    ) as f:
                        print(f.read())
                else:
                    print("Access denied.")

            else:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=os.getcwd(),
                    env=shell_env,
                    text=True,
                    capture_output=True
                )

                if result.stdout:
                    print(result.stdout, end="")

                if result.stderr:
                    print(result.stderr, end="")

        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    shell()