from command import Command
from typing import *
import queue
import threading
from alive_progress import alive_bar
import settings
import time

import modules.cert as cert
from logger import *

class CMD(Command):
    def __init__(self):
        super().__init__(
            "Domain Inference",
            "inferedomain",
            [
                "infdom",
                "id",
            ]
        )

    def domainExtractThread(self, q: queue.Queue, output: Dict):
        while (True):
            try:
                addr = q.get(timeout=3)
            except queue.Empty:
                break

            try:
                if (":" in addr):
                    crt = cert.getCert(addr.split(":")[0], port=int(addr.split(":")[1]))
                else:
                    crt = cert.getCert(addr)
            except Exception as e:
                if (settings.VERBOSE): logErr(str(addr) + " - " + str(e))
                output[addr] = None
                continue
        
            try:
                domains = cert.getDomainsFromCert(crt)
                log(f"{str(addr)} - {str(domains)}")
                output[addr] = domains
            except Exception as e:
                output[addr] = None
                if (settings.VERBOSE): logErr(str(addr) + " - " + str(e))

    def run(self, addresses: List[str]):
        res = {}

        q = queue.Queue()
        for addr in addresses:
            q.put(addr)

        threads = []
        for x in range(min(settings.THREADS, len(addresses))):
            t = threading.Thread(target=self.domainExtractThread, args=(q, res,))
            threads.append(t)

            t.start()

        with alive_bar(len(addresses)) as bar:
            done = 0
            lastDone = done

            forceExit = False
            lastUpdate = time.time()

            while (done < len(addresses) or forceExit):
                diff = done - lastDone
                if (diff > 0):
                    bar(diff)
                    lastDone = done

                time.sleep(.1)

                done = len(list(res.keys()))

                if (lastDone != done):
                    lastUpdate = time.time()
                elif (time.time() - lastUpdate > settings.TIMEOUT * 2):
                    break

        filtered = {k: v for k, v in res.items() if v is not None}
        res.clear()
        res.update(filtered)

        return res