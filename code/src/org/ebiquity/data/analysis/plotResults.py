#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on May 18, 2015
@author: Prajit
Usage: python plotResults.py username api_key
'''

import sys
import time
import databaseHandler
import plotly.tools as tls
# Learn about API authentication here: https://plot.ly/python/getting-started
# Find your api_key here: https://plot.ly/settings/api
import plotly.plotly as py
from plotly.graph_objs import *
import json

# This is a plot for Permissions count vs Frequency of apps requesting that many permissions
def generateAppPermissionsRequestedFrequencyHistogram(username, api_key):
    permCountDict = extractAppPermData()
    permCount = []
    permCountFreq = []
    for permissionCount, permissionCountFreq in permCountDict.iteritems():
        permCount.append(permissionCount)
        permCountFreq.append(permissionCountFreq)

    tls.set_credentials_file(username, api_key)
    trace = Bar(
        x=permCount,
        y=permCountFreq,
        name='App frequency',
        marker=Marker(
            color='rgb(55, 83, 109)'
        )
    )
    data = Data([trace])
    layout = Layout(
        title='App Frequency vs Number of Permissions requested',
        xaxis=XAxis(
            title='Number of Permissions requested',
            titlefont=Font(
                size=16,
                color='rgb(107, 107, 107)'
            ),
            tickfont=Font(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        yaxis=YAxis(
            title='App frequency',
            titlefont=Font(
                size=16,
                color='rgb(107, 107, 107)'
            ),
            tickfont=Font(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        legend=Legend(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1
    )
    fig = Figure(data=data, layout=layout)
    plot_url = py.plot(fig, filename='app-perm')
    print "Check out the URL: "+plot_url+" for your plot"
  
def extractAppPermData():
    dbHandle = databaseHandler.dbConnectionCheck() #DB Open

    cursor = dbHandle.cursor()
    sqlStatement = "SELECT * FROM `app_perm_count_view`;"
    try:
        cursor.execute(sqlStatement)
        if cursor.rowcount > 0:
            queryOutput = cursor.fetchall()
            permCountDict = {}
            for row in queryOutput:
                permissionCount = row[1]
                if permCountDict.has_key(permissionCount):
                    currentValue = permCountDict[permissionCount]
                    permCountDict[permissionCount] = currentValue + 1
                else:
                    permCountDict[permissionCount] = 1
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise

    dbHandle.close() #DB Close
    
    return permCountDict
    
# This is a plot for Permissions count vs Frequency of apps requesting that many permissions
def generatePermissionsRequestedByAppFrequencyHistogram(username, api_key):
    dbHandle = databaseHandler.dbConnectionCheck() #DB Open

#     crawlUrl(dbHandle, "https://raw.githubusercontent.com/android/platform_frameworks_base/master/core/res/AndroidManifest.xml")    
#     sys.exit(1)

    cursor = dbHandle.cursor()
    sqlStatement = "SELECT * FROM `perm_app_count_view` LIMIT 25;"
    try:
        cursor.execute(sqlStatement)
        if cursor.rowcount > 0:
            queryOutput = cursor.fetchall()
            appCount = []
            permName = []
            for row in queryOutput:
                appCount.append(row[0])
                permName.append(row[1])
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise

    dbHandle.close() #DB Close

    tls.set_credentials_file(username, api_key)
    tracePerm = Bar(
        x=permName,
        y=appCount,
        name='App frequency count',
        marker=Marker(
            color='rgb(55, 83, 100)'
        )
    )
    data = Data([tracePerm])
    layout = Layout(
        title='Permission vs App frequency count',
        xaxis=XAxis(
            title='Permission',
            titlefont=Font(
                size=16,
                color='rgb(107, 107, 107)'
            ),
            tickfont=Font(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        yaxis=YAxis(
            title='App frequency',
            titlefont=Font(
                size=16,
                color='rgb(107, 107, 107)'
            ),
            tickfont=Font(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        legend=Legend(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1
    )
    fig = Figure(data=data, layout=layout)
    plot_url = py.plot(fig, filename='perm-app')
    print "Check out the URL: "+plot_url+" for your plot"

# This is a plot for Goodness of Cluster measure using homogeneity_score, completeness_score
def generateGroundTruthResults(username, api_key, clusterCountList, homogeneityScoreList, completenessScoreList, adjustedRandScoreList, adjustedMutualInfoScoreList, vMeasureScoreList, postfix):
    tls.set_credentials_file(username, api_key)
    trace0 = Bar(
        x=clusterCountList,
        y=homogeneityScoreList,
        name='Homogeneity Score',
        marker=Marker(
            color='rgb(0, 255, 0)'
        )
    )
    trace1 = Bar(
        x=clusterCountList,
        y=completenessScoreList,
        name='Completeness Score',
        marker=Marker(
            color='rgb(255, 0, 0)'
        )
    )
    #data = Data([trace0,trace1])
    if len(adjustedRandScoreList) > 0:
        trace2 = Bar(
            x=clusterCountList,
            y=adjustedRandScoreList,
            name='V Measure Score',
            marker=Marker(
                color='rgb(0, 0, 255)'
            )
        )
        data = Data([trace0,trace1,trace2])
        if len(adjustedMutualInfoScoreList) > 0:
            trace3 = Bar(
                x=clusterCountList,
                y=adjustedMutualInfoScoreList,
                name='Adjusted Mutual Info Score',
                marker=Marker(
                    color='rgb(100, 100, 100)'
                )
            )
            data = Data([trace0,trace1,trace2,trace3])
            if len(adjustedRandScoreList) > 0:
                trace4 = Bar(
                    x=clusterCountList,
                    y=adjustedRandScoreList,
                    name='Adjusted Rand Score',
                    marker=Marker(
                        color='rgb(200, 200, 200)'
                    )
                )
                data = Data([trace0,trace1,trace2,trace3,trace4])
    
    layout = Layout(
        title='Number of Clusters vs Homogeneity and Completeness',
        xaxis=XAxis(
            title='Number of Clusters',
            titlefont=Font(
                size=16,
                color='rgb(107, 107, 107)'
            ),
            tickfont=Font(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        yaxis=YAxis(
            title='Goodness Measures',
            titlefont=Font(
                size=16,
                color='rgb(107, 107, 107)'
            ),
            tickfont=Font(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        legend=Legend(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1
    )
    fig = Figure(data=data, layout=layout)
    name = 'cluster-measures'+postfix
    plot_url = py.plot(fig, filename=name)
    print "Check out the URL: "+plot_url+" for your plot"
  
# This is a plot for Goodness of Cluster measure using silhouette_avg
def generatePlotSilhouette(username, api_key, clusterCountList, silhouetteAvgList, postfix):
    tls.set_credentials_file(username, api_key)
    trace = Bar(
        x=clusterCountList,
        y=silhouetteAvgList,
        name='Silhouette Average Score',
        marker=Marker(
            color='rgb(0, 255, 0)'
        )
    )
    data = Data([trace])
    layout = Layout(
        title='Number of Clusters vs Silhouette Average Score',
        xaxis=XAxis(
            title='Number of Clusters',
            titlefont=Font(
                size=16,
                color='rgb(107, 107, 107)'
            ),
            tickfont=Font(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        yaxis=YAxis(
            title='Silhouette Average Score',
            titlefont=Font(
                size=16,
                color='rgb(107, 107, 107)'
            ),
            tickfont=Font(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        legend=Legend(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1
    )
    fig = Figure(data=data, layout=layout)
    name = 'silhouette-average-score'+postfix
    plot_url = py.plot(fig, filename=name)
    print "Check out the URL: "+plot_url+" for your plot"

def plotSilhouetteSamples(username, api_key, fileToRead, postfix=None):
    evaluatedClusterResultsDict = json.loads(open(fileToRead, 'r').read().decode('utf8'))
    
    clusterCountList = []
    
    silhouetteAvgList = []
    
    for clusterCount, loopInfo in evaluatedClusterResultsDict.iteritems():
        if clusterCount != 'appVectors':
            clusterCountList.append(int(clusterCount.replace("Loop","")))
            clusterInfo = loopInfo[2]
            if "silhouette_avg" in clusterInfo:
                #print "In", clusterCount, "we have silhouette_avg of", clusterInfo["silhouette_avg"]
                silhouetteAvgList.append(float(clusterInfo["silhouette_avg"]))

    #print silhouetteAvgList
    generatePlotSilhouette(username, api_key, clusterCountList, silhouetteAvgList, postfix)

def plotGroundTruthResults(username, api_key, fileToRead, postfix=None):
    evaluatedClusterResultsDict = json.loads(open(fileToRead, 'r').read().decode('utf8'))
    
    clusterCountList = []
    
    homogeneityScoreList = []
    completenessScoreList = []
    adjustedRandScoreList = []
    adjustedMutualInfoScoreList = []
    vMeasureScoreList = []
    
    for clusterCount, loopInfo in evaluatedClusterResultsDict.iteritems():
        if clusterCount != 'appVectors':
            clusterCountList.append(int(clusterCount.replace("Loop","")))
            clusterInfo = loopInfo[1]
            if "adjusted_rand_score" in clusterInfo:
                #print "In", clusterCount, "we have adjusted_rand_score of", clusterInfo["adjusted_rand_score"]
                adjustedRandScoreList.append(float(clusterInfo["adjusted_rand_score"]))
            if "adjusted_mutual_info_score" in clusterInfo:
                #print "In", clusterCount, "we have adjusted_mutual_info_score of", clusterInfo["adjusted_mutual_info_score"]
                adjustedMutualInfoScoreList.append(float(clusterInfo["adjusted_mutual_info_score"]))
            if "homogeneity_score" in clusterInfo:
                #print "In", clusterCount, "we have homogeneity_score of", clusterInfo["homogeneity_score"]
                homogeneityScoreList.append(float(clusterInfo["homogeneity_score"]))
            if "completeness_score" in clusterInfo:
                #print "In", clusterCount, "we have completeness_score of", clusterInfo["completeness_score"]
                completenessScoreList.append(float(clusterInfo["completeness_score"]))
            if "v_measure_score" in clusterInfo:
                #print "In", clusterCount, "we have v_measure_score of", clusterInfo["v_measure_score"]
                vMeasureScoreList.append(float(clusterInfo["v_measure_score"]))

    #print clusterCountList, homogeneityScoreList, completenessScoreList, adjustedRandScoreList, adjustedMutualInfoScoreList, vMeasureScoreList
    generateGroundTruthResults(username, api_key, clusterCountList, homogeneityScoreList, completenessScoreList, adjustedRandScoreList, adjustedMutualInfoScoreList, vMeasureScoreList, postfix)

def main(argv):
    if len(sys.argv) != 3:
        sys.stderr.write('Usage: python plotResults.py username api_key\n')
        sys.exit(1)

    startTime = time.time()
    generateAppPermissionsRequestedFrequencyHistogram(sys.argv[1], sys.argv[2])
    generatePermissionsRequestedByAppFrequencyHistogram(sys.argv[1], sys.argv[2])
    executionTime = str((time.time()-startTime)*1000)
    print "Execution time was: "+executionTime+" ms"

if __name__ == "__main__":
    sys.exit(main(sys.argv))
