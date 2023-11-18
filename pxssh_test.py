#!/usr/bin/python3
# pxssh を利用した "su -" のテスト
import sys
import re

from pexpect import pxssh

def login_ssh(server: str, username: str, password: str):
    # ログイン情報を設定しSSHサーバーにログイン
    ssh = pxssh.pxssh(options={
                    "StrictHostKeyChecking": "no",
                    "UserKnownHostsFile": "/dev/null"})

    # プロンプトの設定
    ssh.UNIQUE_PROMPT = r"[\$\#] "
    ssh.PROMPT = ssh.UNIQUE_PROMPT
    ssh.PROMPT_SET_SH = r"PS1='\$ '"
    ssh.PROMPT_SET_CSH = r"set prompt='\$ '"
    ssh.PROMPT_SET_ZSH = "prompt restore;\nPS1='%(!.#.$) '"

    ssh.login(server=server,
            username=username,
            password=password,
            port=22)
    print(ssh.before.decode(encoding='utf-8'), flush=True, end="")
    print(ssh.after.decode(encoding='utf-8'), flush=True, end="")
    return ssh

def sendline_and_print(ssh, command: str):
    print(f"{command}")
    ssh.sendline(command)

def run_command(ssh, command: str):
    sendline_and_print(ssh, command)

    # プロンプトが表示されるまで待つ
    while True:
        index = ssh.expect_list(
            [
                re.compile(r".*(#|\$) ".encode()),   # root ユーザーのプロンプト
                re.compile(r"\n".encode()),
            ], timeout = 10)
        print(ssh.before.decode(encoding='utf-8'), flush=True, end="")
        print(ssh.after.decode(encoding='utf-8'), flush=True, end="")
        if index == 0:
            break

def send_commands(ssh):
    run_command(ssh, "touch test.txt")
    run_command(ssh, "ls -l")

def switch_to_root(ssh, root_pass: str):
    sendline_and_print(ssh, "su -")

    # rootのパスワードを入力するプロンプトが表示されるまで待つ
    ssh.expect(r".*: ")
    print(ssh.before.decode(encoding='utf-8'), flush=True, end="")
    print(ssh.after.decode(encoding='utf-8'), flush=True, end="")

    ssh.sendline(root_pass)

    # root ユーザーのプロンプトが表示されるまで待つ
    index = ssh.expect_list(
        [
            re.compile(r".*# ".encode()),   # root ユーザーのプロンプト
            re.compile(r"su: .*".encode()), # "su: Authentication failure" or "su: 認証失敗"
        ], timeout = 10)
    if index != 0:
        print("failed to switch to root")
        sys.exit(1)
    print(ssh.before.decode(encoding='utf-8'), flush=True, end="")
    print(ssh.after.decode(encoding='utf-8'), flush=True, end="")

def send_commands_root(ssh):
    run_command(ssh, "ls -l")
    run_command(ssh, "find /etc")

    run_command(ssh, "id")
    run_command(ssh, "exit")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(f"Usage: python3 {sys.argv[0]} <server> <username> <password> <root_password>")
        sys.exit(1)

    server = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    root_pass = sys.argv[4]

    ssh = login_ssh(server, username, password)
    send_commands(ssh)
    switch_to_root(ssh, root_pass=root_pass)
    send_commands_root(ssh)

    ssh.logout()
