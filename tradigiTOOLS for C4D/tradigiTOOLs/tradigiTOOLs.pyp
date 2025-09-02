'''

tradigiTOOLS for C4D by Bret Bays, Dimos Vrysellas, and Charles Wardlaw.  
Copyright 2011 FUNhouse Interactive/Circus Ink Entertainment Ltd.

'''
import os
import decimal
import c4d
from decimal import *
from c4d import gui, bitmaps

import c4d.documents
import c4d.plugins

TRADIGITOOLS_DIALOG=10001
SCROLL_GROUP=10002
MAIN_GROUP=10003
KEYS_GROUP=10004
KEY_BUTTON_GROUP=10005
KEY_BUTTON_5=10006
KEY_BUTTON_10=10007
KEY_BUTTON_25=10008
KEY_BUTTON_50=10009
KEY_BUTTON_75=10010
KEY_BUTTON_90=10011
KEY_BUTTON_95=10012
PERCENT_SLIDER=10013
KEY_MODE_GROUP=10014
OVERWRITE_MODE=10015
RIPPLE_MODE=10016
SET_KEY_BUTTON=10017
TIMING_GROUP=10018
MOVE_TO_NEXT_BOX=10019
TIMING_BUTTONS_GROUP=10020
TIMING_FAME_1=10021
TIMING_FAME_2=10022
TIMING_FAME_3=10023
TIMING_FAME_4=10024
TIMING_FAME_5=10025
TIMING_FAME_6=10026
INSERT_FRAMES_GROUP=10027
REMOVE_2_FRAMES=10028
REMOVE_1_FRAME=10029
INSERT_1_FRAME=10030
INSERT_2_FRAMES=10031
INCREMENT_GROUP=10032
INCREMENT_BOX=10033
INCREMENT_TEXT_EDIT=10034
RETIME_BUTTON=10035
AUTO_GROUP=10036
AUTO_CHECKBOX=10037
AUTO_EDIT_TEXT=10038
QUESTION_BUTTON=10039
CAMERA_GROUP=10040
SWAP_CAM_BUTTON=10041
LINK_CAM_GROUP=10042
LINK_GROUP=10043
SHOT_CAM_LINK=10044
CREATE_CAM_BUTTON=10045
QUICK_GROUP=10046
KEY_TYPE_GROUP=10047
RANGE_CHECK=10048
STEPPED_BUTTON=10049
LINEAR_BUTTON=10050
SPLINE_BUTTON=10051
INTERP_DROPDOWN=10052
EDITOR_GROUP=10053
F_CURVE_BUTTON=10054
KEYS_BUTTON=10055
SAVE_INCREMENTAL_BUTTON=10056
CREATE_PREVIEW_BUTTON=10057
CONSOLE_GROUP=10058
CONSOLE_TEXT=10059
CLEAR_BUTTON=10060

#Define the Plugin ID
PLUGIN_ID=1026790



#Begin helpful function definitions

    

def SaveInc():
    c4d.CallCommand(600000051)

def lerp(objA, objB, percent):
    val=objA+(objB-objA)*percent
    return val


def OpenFCurve():
    #Open the Timeline(2)
    c4d.CallCommand(465001511)

    #Set it to F-Curve Mode
    c4d.CallCommand(465001190)

    #Display Only Selected Objects
    if c4d.IsCommandChecked(465001052) is False:
        c4d.CallCommand(465001052)

def OpenKeys():
    #Open the Timeline
    c4d.CallCommand(465001510)

    #Set it to Keys Mode
    c4d.CallCommand(465001191)

def CreateShotCam():
    doc=c4d.documents.GetActiveDocument()
    doc.StartUndo()
    cam=doc.SearchObject("ShotCam")

    if cam is None:
        cam=doc.GetActiveBaseDraw()[c4d.BASEDRAW_DATA_CAMERA]

        ShotCam=c4d.BaseObject(c4d.Ocamera)
        ShotCam.SetName("ShotCam")
        ShotCam.SetMg(cam.GetMg())
        doc.InsertObject(ShotCam)
        doc.AddUndo(c4d.UNDOTYPE_NEW, ShotCam)
        doc.EndUndo()
        c4d.EventAdd()
        return ShotCam
    else:
        doc.EndUndo()
        c4d.EventAdd()
        return cam

def SetSlider(self, num):
    self.SetReal(PERCENT_SLIDER, num, min=0, max=1, step=.01)

class tradigiTOOLSDialog(gui.GeDialog):

    doc=None
    curve=None
    key=None
    bt=None
    btFrame=None
    Prevkey=None
    Nextkey=None
    value=None
    MoveKey=None

    def About(self):
        c4d.gui.MessageDialog("tradigiTOOLS for C4D by Bret Bays, Dimos Vrysellas, and Charles Wardlaw.\n  Copyright 2011 FUNhouse Interactive/Circus Ink Entertainment Ltd.")

    def BrowseRD(self, rd, l, children):
        if not rd: return
        l.append(rd)

        self.BrowseRD(rd.GetNext(), l, children)
        if children:
            self.BrowseRD(rd.GetDown(), l, children)

    def InsertFrames(self, numb, ex=False):
        #self.doc.StartUndo()
        fps=self.doc.GetFps()
        self.curve=[]
        self.key=[]
        self.bt=[]
        self.btFrame=[]
        self.MoveKey=[]
        objList=self.doc.GetSelection()
        
        if len(objList)==0:
            self.SetString(CONSOLE_TEXT, "No Objects Selected!")            
            return
        else:
            for q, x in enumerate(objList):
                trax=x.GetCTracks()
                self.doc.AddUndo(c4d.UNDOTYPE_CHANGE, objList[q])    
                for i,cur in enumerate(trax):
                    self.curve.insert(i, cur.GetCurve())
                    s=0
                    while s<(self.curve[i].GetKeyCount()):
                        self.key.insert(s, self.curve[i].GetKey(s))
                        self.bt.insert(s, self.key[s].GetTime())
            
                    
                        if self.bt[s].GetFrame(fps)>self.doc.GetTime().GetFrame(fps):
                            
                            num=(self.bt[s].GetFrame(fps)+(numb))
                            
                            self.bt[s].SetNumerator(num)
                            self.bt[s].SetDenominator(fps)
            
                            self.key[s].SetTime(self.curve[i], self.bt[s])
                            self.MoveKey.append(self.key[s].GetTime())
                        
                        s=s+1
        print self.MoveKey[0]
        if ex is False:
            if self.GetBool(MOVE_TO_NEXT_BOX) is True:
                self.doc.SetTime(self.MoveKey[0])

        c4d.EventAdd(c4d.EVENT_ANIMATE)
        #self.doc.EndUndo()
        return True

    def Tweening(self, val):
        #self.doc.StartUndo()
        fps=self.doc.GetFps()
        self.curve=[]
        self.key=[]
        self.Prevkey=[]
        self.Nextkey=[]
        self.bt=[]
        self.btFrame=[]
        self.value=[]
        numb=val
        WORLD_TL_ID=465001535
        curFrame=self.doc.GetTime()


        objList=self.doc.GetSelection()
        #print len(objList)
        if len(objList)==0:
            self.SetString(CONSOLE_TEXT, "No Objects Selected!")
            return
        else:
            for q, x in enumerate(objList):
                trax=x.GetCTracks()
                self.doc.AddUndo(c4d.UNDOTYPE_CHANGE, objList[q])    
                for i,cur in enumerate(trax):
                    self.curve.insert(i, cur.GetCurve())
                    s=0
                    p=0
                    a=0
                    while s<(self.curve[i].GetKeyCount()):
                        #print "S: " + str(s)
                        self.key.insert(s, self.curve[i].GetKey(s))
                        self.bt.insert(s, self.key[s].GetTime())
            
                        if self.bt[s].GetFrame(fps)<curFrame.GetFrame(fps):
                            self.Prevkey.insert(p, self.key[s])
                            p=p+1
                            s=s+1
                    
                        elif self.bt[s].GetFrame(fps)>curFrame.GetFrame(fps):
                            if self.Prevkey[p-1].GetTime().GetFrame(fps)==curFrame.GetFrame(fps):
                                bt2=self.bt[s]
                                newFrame=bt2.GetFrame(fps)+1
                                bt2.SetNumerator(newFrame)
                                bt2.SetDenominator(fps)
                                self.key[s].SetTime(self.curve[i], bt2)
                            self.Nextkey.insert(a, self.key[s])
                            a=a+1
                            s=s+1
                            
                        else:
                            if self.GetBool(RIPPLE_MODE) is True:
                                self.Prevkey.insert(p, self.key[s])
                                #self.InsertFrames(1, True)
##                                c4d.CallCommand(12414)
                                p=p+1
                            s=s+1
                        
                    #print "P: " + str(p-1)
                    #print "A: " + str(0)
                    oldKeyTime=self.Prevkey[p-1].GetTime()
                    oldKeyValue=self.Prevkey[p-1].GetValue()
                    oldKeyInterp=self.Prevkey[p-1].GetInterpolation()
                    #print oldKeyInterp
                    newKeyValue=self.Nextkey[0].GetValue()
                    curValue=lerp(oldKeyValue, newKeyValue, val)
                    SetSlider(self, val)
                    dec=str(self.GetReal(PERCENT_SLIDER)*100)
                    dec2=Decimal(dec).quantize(Decimal('1.'), rounding=ROUND_UP)
                    self.SetString(CONSOLE_TEXT, str(dec2) + "%")
                    #print "Old Value: " + str(oldKeyValue)
                    #print "New Value: " + str(newKeyValue)
                    #print "Cur Value: " + str(curValue)
                    if oldKeyTime.GetFrame(fps)==curFrame.GetFrame(fps):
                        timetemp=self.doc.GetTime()
                        timetempframe=timetemp.GetFrame(fps)+1
                        timetemp.SetNumerator(timetempframe)
                        timetemp.SetDenominator(fps)
                        curKeyDict=self.curve[i].AddKey(timetemp)
                        #print "Ghost"
                        truth=False
                    else:
                        #print "Test"
                        curKeyDict=self.curve[i].AddKey(curFrame)
                        truth=True
                    curKey=curKeyDict["key"]
                    curKey.SetValue(self.curve[i], curValue)
                    curKey.SetInterpolation(self.curve[i], self.doc.FindSceneHook(WORLD_TL_ID)[c4d.TLWORLD_INTER])
                    if self.doc.FindSceneHook(WORLD_TL_ID)[c4d.TLWORLD_CLAMP]==1:
                        curKey.ChangeNBit(c4d.NBIT_CKEY_CLAMP, 1)
                    if self.doc.FindSceneHook(WORLD_TL_ID)[c4d.TLWORLD_AUTO]==1:
                        curKey.ChangeNBit(c4d.NBIT_CKEY_AUTO, 1)


                    #curKey.SetTime(self.curve[i], self.doc.GetTime())

        if self.GetBool(RIPPLE_MODE) is True:   
                
            
            if oldKeyTime.GetFrame(fps)==curFrame.GetFrame(fps):
                time=(oldKeyTime.Get()*c4d.documents.GetActiveDocument().GetFps())+1
                bt=c4d.BaseTime()
                bt.SetNumerator(time)
                bt.SetDenominator(c4d.documents.GetActiveDocument().GetFps())
                self.doc.SetTime(bt)
        
        c4d.EventAdd(c4d.EVENT_ANIMATE)

        #self.doc.EndUndo()


    def Timing(self, valu, ex=False):
        self.doc.StartUndo()
        fps=self.doc.GetFps()
        self.curve=[]
        self.key=[]
        self.bt=[]
        self.btFrame=[]
        self.value=[]
        self.MoveKey=[]
        numb=valu
        objList=self.doc.GetSelection()
        
        if len(objList)==0:
            self.SetString(CONSOLE_TEXT, "No Objects Selected!")
            return
        else:
            for q, x in enumerate(objList):
                trax=x.GetCTracks()
                self.doc.AddUndo(c4d.UNDOTYPE_CHANGE, objList[q])    
                for i,cur in enumerate(trax):
                    self.curve.insert(i, cur.GetCurve())
                    s=0
                    p=0
                    while s<(self.curve[i].GetKeyCount()):
                        
                        self.key.insert(s, self.curve[i].GetKey(s))
                        self.bt.insert(s, self.key[s].GetTime())
            
                        if self.bt[s].GetFrame(fps)<=self.doc.GetTime().GetFrame(fps):
                            val=(self.key[p].GetTime().GetFrame(fps)+numb)
                            
                            p=p+1
                            s=s+1
                    
                        else:
                            
                            self.value.append(self.key[s].GetTime().GetFrame(fps)-val)
             
                            num=(self.bt[s].GetFrame(fps)-self.value[0])
                 
                        
                            self.bt[s].SetNumerator(num)
                            self.bt[s].SetDenominator(fps)
            
                            self.key[s].SetTime(self.curve[i], self.bt[s])
                            self.MoveKey.append(self.key[s].GetTime())
                            s=s+1

        if ex is False:
            if self.GetBool(MOVE_TO_NEXT_BOX) is True:
                self.doc.AddUndo(c4d.UNDOTYPE_CHANGE_SMALL, self.doc)
                self.doc.SetTime(self.MoveKey[0])
        c4d.EventAdd()
        self.doc.EndUndo()

    def SetKeyInterp(self, interp):
        range=self.GetBool(RANGE_CHECK)
        self.doc.StartUndo()
        fps=self.doc.GetFps()
        self.curve=[]
        self.key=[]
        self.bt=[]
        self.btFrame=[]
        self.value=[]
        self.MoveKey=[]
        
        objList=self.doc.GetSelection()
        
        if len(objList)==0:
            self.SetString(CONSOLE_TEXT, "No Objects Selected!")
            return
        else:
            for q, x in enumerate(objList):
                trax=x.GetCTracks()
                self.doc.AddUndo(c4d.UNDOTYPE_CHANGE, objList[q])    
                for i,cur in enumerate(trax):
                    self.curve.insert(i, cur.GetCurve())
                    s=0
                    p=0
                    while s<(self.curve[i].GetKeyCount()):
                        
                        self.key.insert(s, self.curve[i].GetKey(s))
                        self.bt.insert(s, self.key[s].GetTime())

                        if range is True:
                            if (self.bt[s].GetFrame(fps)>=self.doc.GetLoopMinTime().GetFrame(fps) and self.bt[s].GetFrame(fps)<=self.doc.GetLoopMaxTime().GetFrame(fps)):
                                self.key[s].SetInterpolation(self.curve[i], interp)
                        elif range is False:
                            self.key[s].SetInterpolation(self.curve[i], interp)

                        s=s+1
        c4d.EventAdd()
        self.doc.EndUndo()

    def TimingCalc(self):
        #self.doc.StartUndo()
        self.doc=c4d.documents.GetActiveDocument()
        fps=self.doc.GetFps()
        self.curve=[]
        self.key=[]
        self.bt=[]
        self.btFrame=[]
        self.value=[]
        self.MoveKey=[]
        curFrame=self.doc.GetTime().GetFrame(fps)
        objList=self.doc.GetSelection()
        Prevkeys=[]
        Nextkeys=[]
        
        if len(objList)==0:
            #self.SetString(CONSOLE_TEXT, "No Objects Selected!")
            return
        else:
            
            trax=objList[0].GetCTracks()
            if len(trax)==0:
                Sent=""
                c4d.EventAdd()
                self.doc.EndUndo()
                return Sent
            #self.doc.AddUndo(c4d.UNDOTYPE_CHANGE, objList[0])    
            
            self.curve.insert(0, trax[0].GetCurve())
            s=0
            p=0
            q=0
            while s<(self.curve[0].GetKeyCount()):
                
                self.key.insert(s, self.curve[0].GetKey(s))
                self.bt.insert(s, self.key[s].GetTime())
                if (self.key[s].GetTime()<=self.doc.GetTime()):
                    Prevkeys.insert(p, self.key[s])
                    p=p+1                    

                if len(Nextkeys)<=0:
                    if (self.key[s].GetTime()>self.doc.GetTime()):
                        Nextkeys.insert(q, self.key[s])
                        q=q+1
                    

                s=s+1
            PrevFrame=Prevkeys[-1].GetTime().GetFrame(fps)
            
            if len(Nextkeys) == 0:
                Sent=("" + str(PrevFrame) + " on  End")
                #c4d.EventAdd()
                self.doc.EndUndo()
                return Sent
            else:
                NextFrame=Nextkeys[0].GetTime().GetFrame(fps)
                CalcFrame=NextFrame-PrevFrame

                Sent=("" + str(PrevFrame) + " on " + str(CalcFrame))
                #c4d.EventAdd()
                self.doc.EndUndo()
                return Sent

            

        
    
    def SwapCams(self, obj):
        camDoc=c4d.documents.GetActiveDocument()
        if obj is None:
            self.SetString(CONSOLE_TEXT, "No Shot Cam Present!")
            return
        
        bd=camDoc.GetActiveBaseDraw()
        editorcam=bd.GetEditorCamera()
        shotcam=obj
        if bd[c4d.BASEDRAW_DATA_CAMERA]==shotcam:
            bd[c4d.BASEDRAW_DATA_CAMERA]=editorcam
        else:
            bd[c4d.BASEDRAW_DATA_CAMERA]=shotcam
        c4d.EventAdd()
        self.SetString(CONSOLE_TEXT, "")


    
    value=0
    linkslot=None

    def GetInterp(self):
        if self.doc==None:
            return 90000
        else:
            #print "Running GetInterp"
            WORLD_TL_ID=465001535
            if self.doc.FindSceneHook(WORLD_TL_ID)[c4d.TLWORLD_INTER]==c4d.CINTERPOLATION_SPLINE:
                #print "Interpolation: Spline"
                return 90000
            if self.doc.FindSceneHook(WORLD_TL_ID)[c4d.TLWORLD_INTER]==c4d.CINTERPOLATION_LINEAR:
                #print "Interpolation: Linear"
                return 90001
            if self.doc.FindSceneHook(WORLD_TL_ID)[c4d.TLWORLD_INTER]==c4d.CINTERPOLATION_STEP:
                #print "Interpolation: Step"
                return 90002

    def __init__(self):
        print("Successfully Loaded")

    def CreateLayout(self):
        
        self.MenuFlushAll()
        self.MenuSubBegin("About")
        self.MenuAddString(99999,"About tradigiTOOLS")
        self.MenuFinished()

        self.SetTitle("tradigiTOOLS")
        res=c4d.plugins.GeResource()
        res.Init(dir)
        
        #self.SetBool(OVERWRITE_MODE, 1)
        self.LoadDialogResource(TRADIGITOOLS_DIALOG, res, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT)
        self.LayoutFlushGroup(LINK_GROUP)
        self.linkslot=self.AddCustomGui(9999, c4d.CUSTOMGUI_LINKBOX, "Shot Cam Slot", c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 0, 0)
        self.LayoutChanged(LINK_GROUP)
        self.AddChild(INTERP_DROPDOWN,90000, "Spline")
        self.AddChild(INTERP_DROPDOWN,90001, "Linear")
        self.AddChild(INTERP_DROPDOWN,90002, "Stepped")
        #print self.linkslot
        #print "flushed"
        return True
    
    def InitValues(self):
        self.SetReal(PERCENT_SLIDER, 0.5, min=0, max=1, step=.01)

        #self.SetLong(INTERP_DROPDOWN, 9000)
        #self.AddChild(INTERP_DROPDOWN,9000, "Spline")
        #self.AddChild(INTERP_DROPDOWN,9001, "Linear")
        #self.AddChild(INTERP_DROPDOWN,9002, "Stepped")
        #print "INIT VALUES"
        self.SetBool(OVERWRITE_MODE, 1)
        #self.SetBool(RIPPLE_MODE, 0)
        self.SetBool(AUTO_CHECKBOX, 0)
        self.SetLong(INTERP_DROPDOWN, self.GetInterp()) #CHANGE BACK TO BE GET INTERP
        #print self.GetBool(OVERWRITE_MODE)

        return True


        
    def CoreMessage(self, id, bc):
        self.doc=c4d.documents.GetActiveDocument()

        if id==c4d.EVMSG_DOCUMENTRECALCULATED:
            #print "Hey!"
            if self.GetBool(AUTO_CHECKBOX) is True:
                
                self.SetString(AUTO_EDIT_TEXT, self.TimingCalc())
                
            '''
            if self.GetLong(INTERP_DROPDOWN)==90000:
                WORLD_TL_HOOK_ID= 465001535
                self.doc.FindSceneHook(WORLD_TL_HOOK_ID)[c4d.TLWORLD_INTER]=c4d.CINTERPOLATION_SPLINE
                #c4d.EventAdd()
                #c4d.DrawViews(c4d.DRAWFLAGS_FORCEFULLREDRAW)

            elif self.GetLong(INTERP_DROPDOWN)==90001:
                WORLD_TL_HOOK_ID= 465001535
                self.doc.FindSceneHook(WORLD_TL_HOOK_ID)[c4d.TLWORLD_INTER]=c4d.CINTERPOLATION_LINEAR
                #c4d.EventAdd()
                #c4d.DrawViews(c4d.DRAWFLAGS_FORCEFULLREDRAW)
            elif self.GetLong(INTERP_DROPDOWN)==90002:
                WORLD_TL_HOOK_ID= 465001535
                self.doc.FindSceneHook(WORLD_TL_HOOK_ID)[c4d.TLWORLD_INTER]=c4d.CINTERPOLATION_STEP
                #c4d.EventAdd()
                #c4d.DrawViews(c4d.DRAWFLAGS_FORCEFULLREDRAW)
            ''' 
        return True


    def Command(self, id, bc):
        
        self.doc=c4d.documents.GetActiveDocument()
        self.doc.StartUndo()
        
        if id==99999:
            self.About()


        #Click the ? Button-----
        if id==QUESTION_BUTTON:
            self.SetString(AUTO_EDIT_TEXT, self.TimingCalc())

            
        #BEGIN BREAKDOWN BUTTON COMMANDS----------------
        
        #Click the <<< Button
        if id==KEY_BUTTON_5:
            self.Tweening(.05)
            SetSlider(self, .05)


        #Click the << Button
        if id==KEY_BUTTON_10:
            self.Tweening(.1)
            SetSlider(self, .1)

        #Click the < Button
        if id==KEY_BUTTON_25:
            self.Tweening(.25)
            SetSlider(self, .25)

        #Click the <> Button
        if id==KEY_BUTTON_50:
            self.Tweening(.5)
            SetSlider(self, .5)

        #Click the > Button
        if id==KEY_BUTTON_75:
            self.Tweening(.75)
            SetSlider(self, .75)

        #Click the >> Button
        if id==KEY_BUTTON_90:
            self.Tweening(.9)
            SetSlider(self, .9)

        #Click the >>> Button
        if id==KEY_BUTTON_95:
            self.Tweening(.95)
            SetSlider(self, .95)

        if id==PERCENT_SLIDER:
            for index, value in bc:
                print index, value
                print bc.GetId()
            print "-"*30
            if bc.GetBool(c4d.BFM_ACTION_INDRAG) is False:
                print "YEEEEEEEEHAW!!!!"
                self.Tweening(self.GetReal(PERCENT_SLIDER))
##            getValue=self.GetReal(PERCENT_SLIDER)
##            bc=c4d.BaseContainer()
##            state=self.GetInputState(PERCENT_SLIDER, c4d.BFM_INPUT_MOUSELEFT, bc)
##            if state is True:
##                bc.SetReal(0, getValue)
##                print bc[0]




        if id==90000:
            print "9000"
        if id==INTERP_DROPDOWN:
            if self.GetLong(INTERP_DROPDOWN)==90000:
                WORLD_TL_HOOK_ID= 465001535
                self.doc.FindSceneHook(WORLD_TL_HOOK_ID)[c4d.TLWORLD_INTER]=c4d.CINTERPOLATION_SPLINE
                c4d.EventAdd()
                #c4d.DrawViews(c4d.DRAWFLAGS_FORCEFULLREDRAW)

            elif self.GetLong(INTERP_DROPDOWN)==90001:
                WORLD_TL_HOOK_ID= 465001535
                self.doc.FindSceneHook(WORLD_TL_HOOK_ID)[c4d.TLWORLD_INTER]=c4d.CINTERPOLATION_LINEAR
                c4d.EventAdd()
                #c4d.DrawViews(c4d.DRAWFLAGS_FORCEFULLREDRAW)
            elif self.GetLong(INTERP_DROPDOWN)==90002:
                WORLD_TL_HOOK_ID= 465001535
                self.doc.FindSceneHook(WORLD_TL_HOOK_ID)[c4d.TLWORLD_INTER]=c4d.CINTERPOLATION_STEP
                c4d.EventAdd()
                    
        #-----------BEGIN CAMERA GROUP COMMANDS-------------
        #Create Shot Cam Button
        if id==CREATE_CAM_BUTTON:
            Cam=CreateShotCam()
            #print "Cam is: " + str(Cam)
            self.linkslot.SetLink(Cam)
            return True

        #Swap Cam Button
        if id==SWAP_CAM_BUTTON:
            shtcm=self.linkslot.GetLink()
            self.SwapCams(shtcm)
            return True
            
        #-----------BEGIN QUICK BUTTONS GROUP COMMANDS-----------

        #Open F-Curve Button
        if id==F_CURVE_BUTTON:
            OpenFCurve()
            return True

        #Open Keys Button
        if id==KEYS_BUTTON:
            OpenKeys()
            return True

        #Save Incremental
        if id==SAVE_INCREMENTAL_BUTTON:
            SaveInc()
            return True

        #Hardware Preview
        if id==CREATE_PREVIEW_BUTTON:
            RDList=[]
            rd2=None
            activeData=self.doc.GetActiveRenderData()
            rdata=self.doc.GetFirstRenderData()
            self.BrowseRD(rdata, RDList, True)
            for x in RDList:
                if x.GetName()=="Hardware Preview":
                    rd2=x

            if rd2 is None:
                #Do Stuff
                #Make New Render Setting called Hardware Preview
                hpreview=c4d.documents.RenderData()
                hpreview.SetName("Hardware Preview")
                hpreview[c4d.RDATA_RENDERENGINE]=c4d.RDATA_RENDERENGINE_PREVIEWHARDWARE
                hpreview[c4d.RDATA_XRES]=activeData[c4d.RDATA_XRES]/2.0
                hpreview[c4d.RDATA_YRES]=activeData[c4d.RDATA_YRES]/2.0

                hpreview[c4d.RDATA_FILMASPECT]=activeData[c4d.RDATA_FILMASPECT]
                hpreview[c4d.RDATA_PIXELASPECT]=activeData[c4d.RDATA_PIXELASPECT]
                hpreview[c4d.RDATA_FRAMERATE]=activeData[c4d.RDATA_FRAMERATE]

                hpreview[c4d.RDATA_FORMAT]=c4d.FILTER_MOVIE
                hpreview[c4d.RDATA_FRAMESEQUENCE]=c4d.RDATA_FRAMESEQUENCE_PREVIEWRANGE
                hpreview[c4d.RDATA_FRAMERATE]=self.doc.GetFps()
                docname=c4d.documents.GetActiveDocument().GetDocumentName()
                docname=docname[0:-4]
                hpreview[c4d.RDATA_PATH]=str(docname) + "_animblast.mov"
          
                
                self.doc.InsertRenderData(hpreview)
                self.doc.SetActiveRenderData(hpreview)
                c4d.CallCommand(12099)      
                c4d.EventAdd()
                #Render

            else:
                #Set this to be the active Render Setting Preset
                self.doc.SetActiveRenderData(rd2)
                c4d.CallCommand(12099)
                c4d.EventAdd()
                #Render
            return True


        if id==STEPPED_BUTTON:
            print "ID", id
            self.SetKeyInterp(c4d.CINTERPOLATION_STEP)
            c4d.EventAdd()
            c4d.DrawViews(c4d.DRAWFLAGS_FORCEFULLREDRAW)

        if id==LINEAR_BUTTON:
            print "ID", id
            self.SetKeyInterp(c4d.CINTERPOLATION_LINEAR)
            c4d.EventAdd()
            #c4d.DrawViews(c4d.DRAWFLAGS_FORCEFULLREDRAW)
        if id==SPLINE_BUTTON:
            print "ID", id
            self.SetKeyInterp(c4d.CINTERPOLATION_SPLINE)
            c4d.EventAdd()
            #c4d.DrawViews(c4d.DRAWFLAGS_FORCEFULLREDRAW)
        #-----------BEGIN CONSOLE COMMANDS-----------------
        #Clear the Console Button
        if id==CLEAR_BUTTON:
            self.SetString(CONSOLE_TEXT, "")
            return True
        
        doc2=c4d.documents.GetActiveDocument()
        doc2.StartUndo()

            
        #-----------BEGIN INSERT FRAMES COMMANDS--------------


        #Insert TWO FRAMES(+2F) BUTTON-------
        if id==INSERT_2_FRAMES:
            self.InsertFrames(2)
            return True

        #Insert ONE FRAME(+1F) BUTTON-------
        if id==INSERT_1_FRAME:
            self.InsertFrames(1)
            return True

        #Subtract ONE FRAME(-1F) BUTTON-------
        if id==REMOVE_1_FRAME:
            self.InsertFrames(-1)
            return True

        #Subtract TWO FRAMES(-2F) BUTTON-------
        if id==REMOVE_2_FRAMES:
           self.InsertFrames(-2)
           return True

        #(6F) BUTTON-------
        if id==TIMING_FAME_6:
            self.Timing(6)
            return True

        #(5F) BUTTON-------
        if id==TIMING_FAME_5:
            self.Timing(5)
            return True

        #(4F) BUTTON-------
        if id==TIMING_FAME_4:
            self.Timing(4)
            return True

        #(3F) BUTTON-------
        if id==TIMING_FAME_3:
            self.Timing(3)
            return True

        #(2F) BUTTON-------
        if id==TIMING_FAME_2:
            self.Timing(2)
            return True

        #(1F) BUTTON-------
        if id==TIMING_FAME_1:
            self.Timing(1)
            return True

        if id==SET_KEY_BUTTON:
            c4d.CallCommand(12410)
            return True

        if self.GetBool(INCREMENT_BOX) is True:
            if id==RETIME_BUTTON:
                self.InsertFrames(int(self.GetString(INCREMENT_TEXT_EDIT)))
                return True
            return True
        if self.GetBool(INCREMENT_BOX) is False:
        #(Retime) BUTTON-------
            if id==RETIME_BUTTON:
                self.Timing(int(self.GetString(INCREMENT_TEXT_EDIT)))
                return True
            return True

        
        self.doc.EndUndo()

class tradigiTOOLS(c4d.plugins.CommandData):
    dialog = None
    file = None

    def Execute(self, doc):
        if self.dialog is None:
            self.dialog=tradigiTOOLSDialog()
        self.dialog.doc=doc
        j=self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaulth=575, defaultw=10)

        return True

    def RestoreLayout(self, sec_ref):
        if self.dialog is None:
            self.dialog=tadigiTOOLSDialog()
        return self.dialog.Restore(pluginid=PLUGIN_ID, secret=sec_ref)



if __name__ == "__main__":

    dir, file = os.path.split(__file__)
    bmp = bitmaps.BaseBitmap()
    bmp.InitWith(os.path.join(dir, "res", "tradigiTOOLS_32X32_vs02.png"))
    c4d.plugins.RegisterCommandPlugin(PLUGIN_ID, "tradigiTOOLS", 0, bmp, "Creates in between keys or breakdown keys while animating", tradigiTOOLS())

