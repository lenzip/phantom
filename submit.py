#!/usr/bin/python


import sys
import os
import commands
from commands import getstatusoutput
import datetime
import argparse
import datetime
import math



def replaceParameterInFile (inputFile, outputFile, substitute): 
    f = open (inputFile)
    s = f.read ()
    f.close ()
    for k,v in substitute.items () :
        s = s.replace (k, v)
    f = open (outputFile, 'w')
    f.write (s)
    f.close ()


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----


def execute (command) :
    print 'running:'
    print command
    retCode = getstatusoutput (command)
    for ri in retCode: print ri


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----


if __name__ == '__main__':

    parser = argparse.ArgumentParser (description = 'run phantom productions on lxplus')
    parser.add_argument('-q', '--queue'    , default= '1nw',    help='batch queue [1nw]')
    parser.add_argument('-m', '--mass'     , default= '126',    help='Higgs mass [126]')
    parser.add_argument('-w', '--width'    , default= 0.00421,  type = float, help='Higgs width []')
    parser.add_argument('-l', '--scaling'  , default= 1.,       type = float, help='squared coupling modifier [1]')
    parser.add_argument('-s', '--step'     , default= '1',      help='production step [1]')
    parser.add_argument('-t', '--template' , default= 'none',   help='input template file [none]')
    parser.add_argument('-f', '--folder'   , default= 'none',   help='local folder name [from the date]')
    parser.add_argument('-c', '--channel'  , default= 'none',   help='production channel (list of leptons)')
    parser.add_argument('-b', '--base'  , default= '/afs/cern.ch/user/l/lenzip/work/phantom/CMSSW_8_0_26_patch1/work/phantom_1_2_8_nc1/',   help='base dir for phandom installation')
    
    args = parser.parse_args ()

#    if args.folder == 'none' and args.step == '2' or :
#        print 'file', args.template, 'not found'
#        print 'please provide an existing template file with relative path'
#        sys.exit (1) 

    if not args.step == '3':
        if args.template == 'none':
            print 'please provide the name of the template file with relative path'
            sys.exit (1) 
        elif not os.path.exists (args.template) :
            print 'file', args.template, 'not found'
            print 'please provide an existing template file with relative path'
            sys.exit (1) 


    substitute = {
        'HMASS_TEMP':  args.mass, 
        'HCOUP_TEMP':  str (math.sqrt(args.scaling)),
        'HWIDTH_TEMP': str (args.width * args.scaling)
        }


    if args.step == '1' :
        # generate the grids
        # ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 
        if args.folder == 'none' :
            args.folder = os.getcwd () + '/grid_' + datetime.datetime.now().strftime('%y-%m-%d-%H-%M')
        else :
            args.folder = os.getcwd () + '/grid_' + args.folder    
        if os.path.exists (args.folder) :
            print 'folder', args.folder, 'exists, quitting'
            sys.exit (1)
        if args.channel == 'none' :
            print 'production channel missing'
            sys.exit (1)
            
        getstatusoutput ('mkdir ' + args.folder)
        replaceParameterInFile (args.template, args.folder + '/r.in', substitute)
        
        command = './setupdir.pl -b '+args.base 
        command += ' -d ' + args.folder
        command += ' -t ' + args.folder + '/r.in'
        command += ' -i "' + args.channel + '" -q ' + str (8 - len (args.channel.split ())) 
        command += ' -s LSF -n ' + args.queue

        execute (command)
        execute ('source ' + args.folder + '/LSFfile')
        execute ('bjobs')
    elif args.step == '2' :
        # generate the events
        # ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 
        if args.folder == 'none' :
            print 'please provide a folder name (without the "gen_" prefix)'
            sys.exit (1)
        gridFolder = os.getcwd () + '/grid_' + args.folder    
        genFolder  = os.getcwd () + '/gen_'  + args.folder    
        if os.path.exists (genFolder) :
            print 'folder', genFolder, 'exists, quitting'
            sys.exit (1)
        if not os.path.exists (gridFolder) :
            print 'folder', gridFolder, 'does not exist, quitting'
            sys.exit (1)
        getstatusoutput ('mkdir ' + genFolder)
        replaceParameterInFile (args.template, genFolder + '/r.in', substitute)

        substitute_step2 = {
            'GRID_FOLDER_TEMP': gridFolder, 
            'GEN_FOLDER_TEMP' : genFolder,
            'QUEUE_TEMP'      : args.queue,
            'TEMPLATE_TEMP'   : genFolder + '/r.in',
            'BASE_FOLDER'     : args.base
            }
        replaceParameterInFile ('submit_step2.sh', 'gen_' + args.folder + '.sh', substitute_step2)
        execute ('source ./gen_' + args.folder + '.sh')
        execute ('bjobs')
    elif args.step == '3' :
        # generate the events
        # ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 
        if args.folder == 'none' :
            print 'please provide a folder name (without the "gen_" prefix)'
            sys.exit (1)
        gridFolder = os.getcwd () + '/grid_' + args.folder    
        genFolder  = os.getcwd () + '/gen_'  + args.folder    
        if not os.path.exists (genFolder) :
            print 'folder', genFolder, 'does not exist, quitting'
            sys.exit (1)
        if not os.path.exists (gridFolder) :
            print 'folder', gridFolder, 'does not exist, quitting'
            sys.exit (1)
        command = 'cd ' + gridFolder + '; grep SIGMA */run.out > res ; '
        command += args.base+'/tools/totint.exe > result '
        print command
        execute (command)
                
        command = 'cd ' + genFolder + '; grep -A 1 total\ integral gen*/run.o* > res ; '
        command += '/afs/cern.ch/user/l/lenzip/work/phantom/CMSSW_8_0_26_patch1/work/phantom_1_2_8_nc1/tools/gentotint.exe > result '
        print command
        execute (command)
        
        print '---> cross section from grids:'
        execute ('tail -n 1 ' + gridFolder + '/result')
        print '---> cross section from generation:'
        execute ('tail -n 1 ' + genFolder + '/result')



