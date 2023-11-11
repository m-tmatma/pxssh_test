#!/usr/bin/python3

import sys

# pexpectライブラリからpxsshモジュールをインポート
from pexpect import pxssh
# timeモジュールをインポート
import time

def login_ssh(server: str, username: str, password: str):
    # ログイン情報を設定しSSHサーバーにログイン
    ssh = pxssh.pxssh(options={
                    "StrictHostKeyChecking": "no",
                    "UserKnownHostsFile": "/dev/null"})
    ssh.login(server=server,
            username=username,
            password=password,
            port=22)
    print("------------before -----------------------------")
    print(ssh.before.decode(encoding='utf-8'), flush=True)
    print("------------after -----------------------------")
    print(ssh.after.decode(encoding='utf-8'), flush=True)
    return ssh

def run_command(ssh, command: str):
    ssh.sendline(command)

    # プロンプトが表示されるまで待つ
    ssh.expect(r".*(#|\$) ")
    print("------------before -----------------------------")
    print(ssh.before.decode(encoding='utf-8'), flush=True)
    print("------------after -----------------------------")
    print(ssh.after.decode(encoding='utf-8'), flush=True)

def send_commands(ssh):
    # テキストファイル「test.txt」を作成する
    run_command(ssh, "touch test.txt")

    # カレントディレクトリのファイルを表示する
    run_command(ssh, "ls -l")

def make_su(ssh, root_pass: str):
    ssh.sendline("su -")

    # rootのパスワードを入力するプロンプトが表示されるまで待つ
    ssh.expect(r".*: ")
    print(ssh.before.decode(encoding='utf-8'), flush=True)
    print(ssh.after.decode(encoding='utf-8'), flush=True)

    ssh.sendline(root_pass)

    # root ユーザーのプロンプトが表示されるまで待つ
    ssh.expect(r".*# ")
    print(ssh.before.decode(encoding='utf-8'), flush=True)
    print(ssh.after.decode(encoding='utf-8'), flush=True)

def send_commands_root(ssh):
    run_command(ssh, "ls -l")

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
    make_su(ssh, root_pass=root_pass)
    send_commands_root(ssh)

    # SSHサーバーからログアウト
    ssh.logout()
