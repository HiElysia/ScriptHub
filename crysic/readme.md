
群控初始化

```
    python .\ssh_sync.py exec .\data\ssh.csv "curl -L https://github.com/cysic-labs/phase2_libs/releases/download/v1.0.0/setup_linux.sh > ~/setup_linux.sh && bash ~/setup_linux.sh {address}"
```

群控启动验证者节点

```
    python .\ssh_sync.py exec .\data\ssh.csv "screen -dm bash -c 'cd ~/cysic-verifier/ && bash start.sh'"
```

检查状态

```
    python .\ssh_sync.py exec .\data\ssh.csv "ps aux | grep verifier"
```

