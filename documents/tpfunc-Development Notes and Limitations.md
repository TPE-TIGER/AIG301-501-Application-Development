# Development Notes and Limitations

## Notes

### Termination of child process using `subprocess`

#### Applicable Products
| Product | Version |
| ------- | ------- |
| AIG-301 | 1.5 |
| AIG-501 | 1.3 |

When using `subprocess` to execute in shell mode, the termination of the child process must be handle if it won't return immediatly.

For example, the following function program won't be stopped by RESTful API or command `tpfunc stop <name>`:
* package.json
    ```json
    {
    "name": "stress-ng",
    "enabled": true,
    "trigger": {
        "driven": "timeDriven",
        "timeDriven": {
        "mode": "boot",
        "intervalSec": 1,
        "cronJob": ""
        }
    },
    "expose": {},
    "executable": {
        "language": "python"
    },
    "params": {}
    }
    ```
* index.py
    ```python
    #!/usr/bin/python

    import subprocess

    if __name__ == "__main__":
        print(subprocess.run("sleep 1000", shell=True, check=True))
    ```

To avoid the scenario, you need to catch the signal and stop child process gracefully. Here's the modification of index.py:
```python
#!/usr/bin/python

import os
import signal
import subprocess
import time

run = True

def sigterm_handler(_signo, _stack_frame):
    global run
    run = False

if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigterm_handler)
    signal.signal(signal.SIGTERM, sigterm_handler)

    cmd = "sleep 1000"
    pro = subprocess.Popen(cmd, stdout=subprocess.PIPE,
        shell=True, preexec_fn=os.setsid)

    while run:
        time.sleep(2)
        print("waiting...")
    print("kill child")
    os.killpg(os.getpgid(pro.pid), signal.SIGTERM)
    print("stopped")
```

