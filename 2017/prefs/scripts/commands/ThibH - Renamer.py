class ThibHRenamer(object):
    def __init__(self):
        pass

    def basic_rename(self, *args):
        
        print("---- ThibH Renamer ----")

        selected_objects = mc.ls(sl=True)
        name = mc.textField("renameTextField", query=True, text=True)
        
        try:
            pad_pattern = re.search('[#]+', name).group()
            pad_length = len(pad_pattern)
        except:
            pad_pattern = ""
            pad_length = 0
            
           
        for i, obj in enumerate(selected_objects):       
            
            
            if pad_length > 0:
                mc.rename(obj, name.replace(pad_pattern, str(i).zfill(pad_length)))
                print("Renamed object '{0}' to '{1}'".format(obj, name.replace(pad_pattern, str(i).zfill(pad_length))))    
            else:
                if "," in name:
                    search = name.split(",")[0].rstrip()
                    replace = name.split(",")[1].lstrip()
                    mc.rename(obj, obj.replace(search, replace))
                if len(selected_objects) == 1:
                    mc.rename(obj, name)
                    print("Renamed object '{0}' to '{1}'".format(obj, name.replace(pad_pattern, str(i).zfill(pad_length))))    
                else:
                    mc.rename(obj, name + str(i))
                    print("Renamed object '{0}' to '{1}'".format(obj, name.replace(pad_pattern, str(i).zfill(pad_length))))    
                    

    def add_prefix_suffix(self, prefixOrSuffix, *args):
        print("---- ThibH Renamer ----")

        selected_objects = mc.ls(sl=True)
        text = mc.textField("renameTextField", query=True, text=True)

        try:
            pad_pattern = re.search('[#]+', text).group()
            pad_length = len(pad_pattern)
        except:
            pad_pattern = ""
            pad_length = 0

        for i, obj in enumerate(selected_objects):
            if pad_length > 0:
                if prefixOrSuffix == "prefix":
                    mc.rename(obj, text.replace(pad_pattern, str(i).zfill(pad_length)) + obj)
                    print("Renamed object '{0}' to '{1}'".format(obj, text.replace(pad_pattern, str(i).zfill(pad_length)) + obj))
                elif prefixOrSuffix == "suffix":
                    mc.rename(obj, obj + text.replace(pad_pattern, str(i).zfill(pad_length)))
                    print("Renamed object '{0}' to '{1}'".format(obj, obj + text.replace(pad_pattern, str(i).zfill(pad_length))))            
            else:
                if prefixOrSuffix == "prefix":
                    mc.rename(obj, text + obj)
                    print("Renamed object '{0}' to '{1}'".format(obj, text + obj))
                elif prefixOrSuffix == "suffix":
                    mc.rename(obj, obj + text)
                    print("Renamed object '{0}' to '{1}'".format(obj, obj + text))


    def createGUI(self):
        if mc.window("ThibHRenamer", query=True, exists=True):
            mc.deleteUI("ThibHRenamer")
        mc.window("ThibHRenamer", title="ThibH Renamer", mxb=False, width=500, height=175, sizeable=False)
        
        mc.frameLayout("mainLayout", label="ThibH Renamer")
        
        mc.text("- use # for padding")
        mc.text("- for Search and Replace, use this format: searchString, replaceString")
        
        mc.textField("renameTextField", enterCommand=self.basic_rename, alwaysInvokeEnterCommandOnReturn=True)
        mc.button("renameButton", label="Rename", command=self.basic_rename)
        
        mc.gridLayout("prefixSuffixLayout", numberOfColumns=2, cellWidth=249)
        
        mc.button("prefixButton", label="Add prefix", command=partial(self.add_prefix_suffix, "prefix"))
        mc.button("suffixButton", label="Add suffix", command=partial(self.add_prefix_suffix, "suffix"))
        
        mc.showWindow("ThibHRenamer")
        mc.window("ThibHRenamer", edit=True, width=500, height=175)


renamer = ThibHRenamer()
renamer.createGUI()