import main, utils
reload(main)
reload(utils)

global contextConnector_win
try:
	contextConnector_win.close()
	contextConnector_win.deleteLater()
except: pass

contextConnector_win = main.MainWindow() 
contextConnector_win.show()

contextConnector_win.updateSelection()