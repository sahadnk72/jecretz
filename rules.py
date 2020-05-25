
# Add custom regular expressions here

custom_rules = {
	"json_data": "\"?(?:[c|C][l|L][i|I][e|E][n|N][t|T][i|I][d|D]|[p|P][a|A][s|S][s|S][w|W][o|O][r|R][d|D]|[a|A][u|U][t|T][h|H]|[k|K][e|E][y|Y]|[t|T][o|O][k|K][e|E][n|N]|[s|S][e|E][c|C][r|R][e|E][t|T]|[p|P][w|W][d|D]|[p|P][a|A][s|S][s|S]|[p|P][a|A][s|S][s|S][w|W][d|D])\"?\s?:\s?\"?[a-zA-Z0-9/@#$!%^&*()\[\]{}\\+=-]+\"?",
	"equals": "(?:[A|a][u|U][t|T][h|H]|[p|P][a|A][s|S][s|S][w|W][o|O][r|R][d|D]|[k|K][e|E][y|Y]|[t|T][o|O][k|K][e|E][n|N]|[s|S][e|E][c|C][r|R][e|E][t|T]|[p|P][w|W][d|D]|[p|P][a|A][s|S][s|S]|[p|P][a|A][s|S][s|S][w|W][d|D])\s?=\s?[a-zA-Z0-9/@#$!%^&*()\[\]{}]+",
	"headers": "(?:[A|a]uthorization|[t|T]oken|[a|A]ccess-[t|T]oken|access_token|[a|A]uth_token|[K|k]ey|[s|S][e|E][c|C][r|R][e|E][t|T]|[c|C][o|O][o|O][k|K][i|I][e|E]|[p|P][w|W][d|D]|[p|P][a|A][s|S][s|S]|[p|P][a|A][s|S][s|S][w|W][d|D])\s?:\s?(?:Bearer\s)?[a-zA-Z0-9.\-=/+_\\!]+",
	"jwt": "eyJ[a-zA-Z0-9.=/+-]+",
	#"credit_cards": "(\d{4}.?){3}\d{4}",
	"mongo": "(?:mongodb://)(?:[a-zA-Z0-9\@_:-]{1,50}\.)+[a-zA-Z0-9]{1, 25}"
}
