from injector import Injector

injector = Injector()

from injector import singleton

from data_processor.steps.transform.execute_sql import ExecuteSQL
from data_processor.steps.save.write import Write
from data_processor.steps.read.read import Read
from data_processor.steps.transform.join_table import JoinTable
from data_processor.steps.transform.join_multi_table import JoinMultiTable
from data_processor.steps.transform.rule_engine import RuleEngine

## Read from constants
injector.binder.bind('ExecuteSQL', to=ExecuteSQL, scope=singleton)
injector.binder.bind('Write', to=Write, scope=singleton)
injector.binder.bind('Read', to=Read, scope=singleton)
injector.binder.bind('JoinTable', to=JoinTable, scope=singleton)
injector.binder.bind('MultiTableJoin', to=JoinMultiTable, scope=singleton)
injector.binder.bind('MultiTableJoin', to=JoinMultiTable, scope=singleton)
injector.binder.bind('RuleEngine', to=RuleEngine, scope=singleton)
