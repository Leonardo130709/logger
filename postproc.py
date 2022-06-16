from ycutils.tb_parser import TBParser

logs = TBParser.detect_logs('logdir')
parser = TBParser(logs[0])
parser.to_csv('summary/mse_loss', suffix_keys='mse_loss')
