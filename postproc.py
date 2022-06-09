from src.tbparser import TBParser

logs_files = TBParser.detect_logs('logdir')
for log in logs_files:
    parser = TBParser(log)
    parser.to_csv('summary/mse_loss', prefix_keys=('mse_loss',))
