import ROOT
import AbstractClasses
from AbstractClasses.ModuleMap import ModuleMap

class TestResult(AbstractClasses.GeneralTestResult.GeneralTestResult):
    def CustomInit(self):
        self.Name='CMSPixel_QualificationGroup_XRayHRQualification_HitOverview_TestResult'
        self.NameSingle='HitOverview'
        self.Attributes['TestedObjectType'] = 'CMSPixel_Module'

    def PopulateResultData(self):
        ROOT.gStyle.SetOptStat(0)

        # initialize module map
        self.ModuleMap = ModuleMap(Name=self.GetUniqueID(), nChips=self.ParentObject.Attributes['NumberOfChips'], StartChip=self.ParentObject.Attributes['StartChip'])
        Directory = self.ParentObject.Attributes['SCurvePaths']['HRSCurves_{Rate}'.format(Rate=self.Attributes['Rate'])]

        for i in self.ParentObject.ResultData['SubTestResults']['Chips'].ResultData['SubTestResults']:
            ChipTestResultObject = self.ParentObject.ResultData['SubTestResults']['Chips'].ResultData['SubTestResults'][i]
            ChipNo = ChipTestResultObject.Attributes['ChipNo']

            SCurveFileName = Directory + '/' + self.ParentObject.ParentObject.HistoDict.get('HighRate', 'SCurveFileName').format(ChipNo=ChipNo)
            SCurveFile = open(SCurveFileName, "r")

            if not SCurveFile:
                raise Exception('Cannot find SCurveFile "%s"'%SCurveFileName)
            else:
                Line = SCurveFile.readline()
                Line = SCurveFile.readline()

                for column in range(self.nCols): #Columns
                    for row in range(self.nRows): #Rows
                        Line = SCurveFile.readline()
                        if Line:
                            LineArray = Line.strip().split()
                            Noise = float(LineArray[1])
                            if 0 < Noise < 2000:
                                self.ModuleMap.UpdatePlot(ChipNo, column, row, Noise)
            SCurveFile.close()

        # draw module map
        if self.ModuleMap:
            self.ModuleMap.SetContour(100)
            self.ResultData['Plot']['ROOTObject'] = self.ModuleMap.GetHistogram()
            if self.ResultData['Plot']['ROOTObject'] and self.ResultData['Plot']['ROOTObject'].GetMaximum() < 600:
                self.ResultData['Plot']['ROOTObject'].GetZaxis().SetRangeUser(0, 600)

            self.ModuleMap.Draw(Canvas=self.Canvas, TitleZ="electrons")

        # save canvas
        self.ResultData['Plot']['Format'] = 'png'
        self.Title = 'Noise {Rate}'.format(Rate=self.Attributes['Rate'])
        self.SaveCanvas()