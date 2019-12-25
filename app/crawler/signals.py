from blinker import Namespace

crawler_signal = Namespace()

scraping_done = crawler_signal.signal('scraping-done')
