#!/usr/bin/python
import statistics


def bestMean(valLst, sigTol=2):
    """Calculate the "best mean" of the list of numbers in valLst by
    calculating the mean, then rejecting values outside of sigTol standard
    deviations from the mean, and re-calculating the mean.
    Returns (bestMean, data) where bestMean is the best mean value and data
    is a dictionary of other information on the calculation.
    NOTE: THIS DOES NOT WORK VERY WELL FOR VERY SMALL SAMPLES - this is because
    stdev increases a lot when you add an outlier (as I found using a 4 sample set).
    """
    listOk = False

    curLst = valLst
    while not listOk:
        meanVal = statistics.fmean(curLst)
        stdVal = statistics.stdev(curLst)
        listOk = True
        newLst = []
        for i in range(0, len(valLst)):
            if (abs(curLst[i] - meanVal) > sigTol*stdVal):
                print("beastMean - item %d rejected: val=%f, mean=%f, std=%f"
                      % (i, curlst[i], meanVal, stdVal))
                listOk = False
            else:
                newLst.append(curLst[i])
        print("Listok=%d" % (listOk))
        if (listOk):
            return(meanVal, {"mean": meanVal,"stdev":stdVal, "validVals":curLst})


if (__name__=="__main__"):
    print("statUtils.main")

    valLst = [5, 10, 15, 20]
    print(bestMean(valLst))
