#! /usr/bin/env python
""" 
Script for selecting the coarse channel to be zoomed for the narrow-band mode.

Author: Paul Prozesky
"""
"""
Revisions:
2011-09-02  PVP Initial version.
"""

import corr, sys, logging

def exit_fail():
    print 'FAILURE DETECTED. Log entries:\n',lh.printMessages()
    print "Unexpected error:", sys.exc_info()
    try:
        c.disconnect_all()
    except: pass
    exit(1)

def exit_clean():
    try:
        c.disconnect_all()
    except: pass
    exit(0)

if __name__ == '__main__':
    from optparse import OptionParser

    p = OptionParser()
    p.set_usage('%prog [options] [CUSTOM_CONFIG_FILE]')
    p.set_description(__doc__)
    p.add_option('-m', '--mixer', dest = 'mixer_sel', type = 'int', default = -1, 
        help = 'Select the unmixed(0) or mixed(1) signal path in the F engine.')
    p.add_option('-c', '--channel', dest = 'channel_sel', type = 'int', default = -1, 
        help = 'Select the coarse channel to be further channelised.')
    opts, args = p.parse_args(sys.argv[1:])
    if args == []:
        config_file = None
    else:
        config_file = args[0]

lh = corr.log_handlers.DebugLogHandler(100)
try:
    print 'Connecting...',
    c = corr.corr_functions.Correlator(config_file = config_file, log_level = logging.INFO, connect = False, log_handler = lh)
    if not c.is_narrowband():
        print 'Can only be run on narrowband correlators.'
        exit_fail()
    c.connect()
    print 'done'

    if opts.mixer_sel > -1:
        print 'Setting mixer to %i...' % opts.mixer_sel,
        corr.corr_functions.write_masked_register(c.ffpgas, corr.corr_nb.register_fengine_coarse_control, mixer_select = True if opts.mixer_sel == 1 else False)
        print 'done.'

    if opts.channel_sel > -1:
        print 'Setting coarse channel to %i...' % opts.channel_sel,
        corr.corr_functions.write_masked_register(c.ffpgas, corr.corr_nb.register_fengine_coarse_control, channel_select = opts.channel_sel)
        print 'done.'

    # print the setup on the fengines
    rv = corr.corr_functions.read_masked_register(c.ffpgas, corr.corr_nb.register_fengine_coarse_control)
    # work out the center frequency of the selected band
    c.config['center_freq'] = float(rv[0]['channel_select']) * float(c.config['bandwidth'])
    for ctr, v in enumerate(rv):
        print "%s: mixer(%d) channel(%d) cf(%.6f Mhz)" % (c.fsrvs[ctr], v['mixer_select'], v['channel_select'], c.config['center_freq'] / 1000000.0)

except KeyboardInterrupt:
    exit_clean()
except:
    exit_fail()
