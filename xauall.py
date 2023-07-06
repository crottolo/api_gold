from tv import main
from queue import Queue
from threading import Thread

NUM_THREADS = 20
q = Queue()

def get_pair():
    global q
    while True:
        pair = q.get()
        try:
            main(pair, '')
        except Exception as e:
            print("errororoeororor: ", e)
            pass
        q.task_done() 
        
if __name__ == '__main__':
    for i in range(NUM_THREADS):
        worker = Thread(target=get_pair)
        worker.daemon = True
        worker.start()
        
    
    # for pair in ['GBPUSD']:
    for pair in ['XAUUSD', 'XAUEUR']:
        q.put(pair, block=False, timeout=None)
        
    q.join()
    print('All tasks are done!')