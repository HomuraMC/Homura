import yaml
from classes.lognk import log
import sys

logger = log.logger

class Config():
	data = {}
	
	def load(self):
		try:
			with open('config.yml') as file:
				Config.data = yaml.safe_load(file)
		except Exception as e:
			logger.error('Exception occurred while loading YAML...', file=sys.stderr)
			logger.error(e, file=sys.stderr)
		return
	
	def save(self,obj):
		with open('config.yml', 'w') as file:
			yaml.dump(obj, file, encoding='utf-8', allow_unicode=True)