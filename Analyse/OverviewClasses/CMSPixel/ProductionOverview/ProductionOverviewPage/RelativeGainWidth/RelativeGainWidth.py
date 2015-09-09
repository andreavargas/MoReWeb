import ROOT
import AbstractClasses
import glob
import json

class ProductionOverview(AbstractClasses.GeneralProductionOverview.GeneralProductionOverview):

    def CustomInit(self):
    	self.Name='CMSPixel_ProductionOverview_RelativeGainWidth'
    	self.NameSingle='RelativeGainWidth'
        self.Title = 'RelativeGainWidth {Test}'.format(Test=self.Attributes['Test'])
        self.DisplayOptions = {
            'Width': 1,
        }
        self.SubPages = []
        self.SavePlotFile = True
        self.Canvas.SetCanvasSize(400,500)


    def GenerateOverview(self):
        ROOT.gStyle.SetOptStat(111210)
        ROOT.gPad.SetLogy(1)

        TableData = []

        Rows = self.FetchData()

        ModuleIDsList = []
        for RowTuple in Rows:
            if not RowTuple['ModuleID'] in ModuleIDsList:
                ModuleIDsList.append(RowTuple['ModuleID'])

        HTML = ""

        HistogramMax = 0.25
        NBins = 120
        Histogram = ROOT.TH1D(self.GetUniqueID(), "", NBins, 0, HistogramMax)

        PlotColor = self.GetTestPlotColor(self.Attributes['Test'])

        Histogram.SetLineColor(PlotColor)
        Histogram.SetFillColor(PlotColor)
        Histogram.SetFillStyle(1001)
        Histogram.GetXaxis().SetTitle("Rel. Gain Width [%]")
        Histogram.GetYaxis().SetTitle("# ROCs")
        Histogram.GetYaxis().SetTitleOffset(1.5)

        NROCs = 0
        for ModuleID in ModuleIDsList:

            for RowTuple in Rows:
                if RowTuple['ModuleID'] == ModuleID:
                    TestType = RowTuple['TestType']

                    if TestType == self.Attributes['Test']:

                        for Chip in range(0, 16):
                            Sigma = self.GetJSONValue([ RowTuple['RelativeModuleFinalResultsPath'], RowTuple['FulltestSubfolder'], 'Chips','Chip%d'%Chip, 'PHCalibrationGain', 'KeyValueDictPairs.json', 'sigma', 'Value'])
                            Mu = self.GetJSONValue([ RowTuple['RelativeModuleFinalResultsPath'], RowTuple['FulltestSubfolder'], 'Chips','Chip%d'%Chip, 'PHCalibrationGain', 'KeyValueDictPairs.json', 'mu', 'Value'])
                            
                            if Sigma is not None and Mu is not None and float(Mu)>0:
                                Histogram.Fill(float(Sigma) / float(Mu))
                                NROCs += 1

                        break
        
        Histogram.Draw("")

        ROOT.gPad.Update()
        PaveStats = Histogram.FindObject("stats")
        PaveStats.SetX1NDC(0.62)
        PaveStats.SetX2NDC(0.83)
        PaveStats.SetY1NDC(0.8)
        PaveStats.SetY2NDC(0.9)
        
        GradeAB = float(self.TestResultEnvironmentObject.GradingParameters['gainB'])
        GradeBC = float(self.TestResultEnvironmentObject.GradingParameters['gainC'])

        PlotMaximum = Histogram.GetMaximum()*1.1
        Histogram.SetMaximum(PlotMaximum)

        CloneHistogram = ROOT.TH1D(self.GetUniqueID(), "", NBins, 0, HistogramMax)
        for i in range(1,NBins):
            if i > GradeAB/HistogramMax*NBins and i < GradeBC/HistogramMax*NBins:
                CloneHistogram.SetBinContent(i, PlotMaximum)
          
        CloneHistogram.SetFillColorAlpha(ROOT.kBlue, 0.12)
        CloneHistogram.SetFillStyle(1001)
        CloneHistogram.Draw("same")

        CloneHistogram2 = ROOT.TH1D(self.GetUniqueID(), "", NBins, 0, HistogramMax)
        for i in range(1,NBins):
            if i >= GradeBC/HistogramMax*NBins:
                CloneHistogram2.SetBinContent(i, PlotMaximum)
          
        CloneHistogram2.SetFillColorAlpha(ROOT.kRed, 0.15)
        CloneHistogram2.SetFillStyle(1001)
        CloneHistogram2.Draw("same")

        CloneHistogram3 = ROOT.TH1D(self.GetUniqueID(), "", NBins, 0, HistogramMax)
        for i in range(1,NBins):
            if i <= GradeAB/HistogramMax*NBins:
                CloneHistogram3.SetBinContent(i, PlotMaximum)
          
        CloneHistogram3.SetFillColorAlpha(ROOT.kGreen+2, 0.1)
        CloneHistogram3.SetFillStyle(1001)
        CloneHistogram3.Draw("same")

        # mean, rms and gauss fit sigma
        GaussFitFunction = ROOT.TF1("GaussFitFunction", "gaus(0)")
        GaussFitFunction.SetParameter(0, Histogram.GetBinContent(Histogram.GetMaximumBin()))
        GaussFitFunction.SetParameter(1, Histogram.GetMean())
        GaussFitFunction.SetParameter(2, Histogram.GetRMS())
        GaussFitFunction.SetParLimits(1,0,1)
        GaussFitFunction.SetParLimits(2,0,0.1)
        Histogram.Fit(GaussFitFunction, "QB0")
        GaussFitSigma = GaussFitFunction.GetParameter(2)
        title = ROOT.TText()
        title.SetNDC()
        title.SetTextAlign(12)
        title.SetTextSize(0.03)
        TitleText = "Mean: %.3f, RMS: %.4f, Gauss-fit sigma: %.4f"%(Histogram.GetMean(), Histogram.GetRMS(), GaussFitSigma)
        title.DrawText(0.15, 0.965, TitleText)

        self.SaveCanvas()

        HTML = self.Image(self.Attributes['ImageFile']) + self.BoxFooter("Number of ROCs: %d"%NROCs)

        AbstractClasses.GeneralProductionOverview.GeneralProductionOverview.GenerateOverview(self)


        ROOT.gPad.SetLogy(0)
        return self.Boxed(HTML)
