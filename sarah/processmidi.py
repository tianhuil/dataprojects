import midi
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

filedir = './Music/'

def make_note_list(pat):
    #loop over tracks.  When a note is turned on, record it in dict active_notes as a pair of
    #{value:start_tick}.  When we read a key off event for that note value, remove it from the
    #active dict, add the end tick to the list [start_tick,value,end_tick] and shove it into
    #the note list by track.
    note_list_by_track = []
    for p in pat:
        notes_this_track = []
        active_notes = {}
        current_tick = 0
        for ev in p:
            if isinstance(ev, midi.events.NoteOnEvent) and ev.data[1] != 0:
                #key down event
                current_tick += ev.tick
#                print "Key down. Value = " + str(ev.data[0]) + ". Tick = " + str(current_tick)
                if ev.data[0] not in active_notes:
                    #simplest case: note is not already on
                    active_notes[ev.data[0]]=current_tick
                else:
                    #pain-in-the-ass case.  note is already on.
                    if isinstance(active_notes[ev.data[0]],int):
                        #key has been activated once previously
                        prev_ticks = [active_notes[ev.data[0]]]
#                        print "One previous activation on tick " + str(prev_ticks)
                    else:
                        #key has been activated multiple times previously
                        prev_ticks = active_notes[ev.data[0]]
#                        print "Previous activations on ticks " + str(prev_ticks)
                    prev_ticks.append(current_tick)
                    active_notes[ev.data[0]] = prev_ticks
#                print "Notes on now are: " + str(active_notes)
#                print "Current tick is now " + str(current_tick)
            elif isinstance(ev, midi.events.NoteOffEvent) or (isinstance(ev, midi.events.NoteOnEvent) and ev.data[1] == 0):
                #key up event
                current_tick += ev.tick
#                print "Key up.  Value = " + str(ev.data[0]) + ". Tick = " + str(current_tick)
#                print "Active notes are " + str(active_notes)
                note_val = ev.data[0]
                tup = current_tick
                if note_val in active_notes:
                    #check to make sure we can't turn off a note that isn't on, because
                    #this apparently happens once in a blue moon
                    if isinstance(active_notes[note_val],int):
                        #simplest case: note was turned on only once
                        tdn = active_notes[note_val]
    #                    print "Removing note " + str(ev.data[0]) + " from the dict."
                        del active_notes[note_val]
                    else:
                        #pain-in-the-ass case.  note was turned on twice.  take the lowest tick
                        #in the list, assign it to tdn, and get rid of it.
                        active_notes[note_val].sort()
                        tdn = active_notes[note_val].pop(0)
                        if len(active_notes[note_val])==1:
                            active_notes[note_val] = active_notes[note_val][0]
    #                    else:                        
    #                        active_notes[ev.data[0]] = lticks
                notes_this_track.append([tdn,note_val,tup])
            else:
                #not a note event
                current_tick += ev.tick
        note_list_by_track.append([pat.index(p),notes_this_track])
    return note_list_by_track


def collapsetracks(note_list_by_track):
    #since the notes are now in [start_tick,value,end_tick] form, this is easier.  We can
    #just concatenate the lists.

    ticks_collapsed = []
    for i in note_list_by_track:
        if len(i[1])<2:
            pass
        else:
            ticks_collapsed += i[1]
    return ticks_collapsed


def get_meas(pattern):
    
    t=[0]*len(pattern)
    for i in range(len(pattern)):
        #tracks
        #print "Track " + str(i)
        for j in range(len(pattern[i])):
            t[i] += pattern[i][j].tick
            #print "Adding " + str(pattern[i][j].tick) + ": total tick count now " + str(t[i])
    #print t
    numticks = max(t)
    
    meas_ticks = [0]
    last_ts_tick = 0
    ticks_passed = 0
    ts_changed = 0
    #print "Resolution = " + str(pattern.resolution)
    for i in pattern[0]:
        if isinstance(i,midi.events.TimeSignatureEvent):
            if i.tick == 0:
    #            ticks_passed += i.tick
                ts_num = i.data[0]
                ts_den = 2**(i.data[1])
                ts_tick = 0

                #print "Time sig = " + str(ts_num) + "/" + str(ts_den) + " at tick " + str(ts_tick)
                idataold = i.data
            else:
                if i.data == idataold:
                    ticks_passed += i.tick
                else:
                    ts_changed = 1
                    ticks_passed += i.tick
                    to_last_ts = ticks_passed-ts_tick
                    #print str(to_last_ts) + " ticks of the last time sig."
                    #print "Tick conversion: " + str(ts_conv)
                    #print ts_num
                    #print ts_conv
                    #print "Measure length is " + str((pattern.resolution * 4/ts_den * ts_num)) + " ticks."
                    num_measures = to_last_ts / (pattern.resolution * 4/ts_den * ts_num)
                    #print str(num_measures) + " measures of the last time sig."
                    #print "Tick now is " + str(ts_tick) + ".  Appending to array: "
                    for j in range(num_measures):
                        meas_ticks.append(ts_tick + (j+1)*pattern.resolution * 4/ts_den * ts_num)
                        #print (ts_tick + (j+1)*pattern.resolution * 4/ts_den * ts_num)
                    ts_num = i.data[0]
                    ts_den = 2**(i.data[1])
                    ts_tick = ticks_passed
                    idataold = i.data
                    #print "Time sig change to " + str(ts_num) + "/" + str(ts_den) + " at tick " + str(ts_tick)
        elif isinstance(i,midi.events.EndOfTrackEvent):
            ticks_passed += i.tick
            #print "End of tempo track at tick " + str(ticks_passed)
            to_last_ts = ticks_passed-ts_tick
            num_measures = to_last_ts / (pattern.resolution * 4/ts_den * ts_num)
            for j in range(num_measures):
                        meas_ticks.append(ts_tick + (j+1)*pattern.resolution * 4/ts_den * ts_num)
                        #print (ts_tick + (j+1)*pattern.resolution * 4/ts_den * ts_num)
        else:
            ticks_passed += i.tick
    if ts_changed == 0:
        meas_ticks = [i*pattern.resolution * 4/ts_den * ts_num for i in range(numticks/(pattern.resolution * 4/ts_den * ts_num))]
    return meas_ticks


def split_on_four_meas(pattern):
#    Redoing for time signature changes.  Possible structure: for loop over all possible ticks?
#    From TimeSignatureEvent, count forward ts_num * pattern.resolution ticks. Did we pass a TimeSignatureEvent?
#    If yes, increment the measure counter, go to the tick where the TSE occurred, get the new ts_num,
#    count forward by new ts_num ticks.
#    "Ornament" is then a note that's shorter than a (ts_den*8)th note - resolution/8?
    slice_list = []
    note_list_by_track = make_note_list(pattern)
    ticks_collapsed = collapsetracks(note_list_by_track)
    meas_ticks = get_meas(pattern)
    #print ticks_collapsed
    ts = np.array(ticks_collapsed)
    testframe = pd.DataFrame(ts,columns=['start_tick','note_val','end_tick'])
    #print testframe

    slice_counter = 0
    stop_early = False
    while slice_counter < len(meas_ticks)/4.0:
        low_bound = meas_ticks[slice_counter*4]
        if (slice_counter+1)*4 < len(meas_ticks):
            if meas_ticks[(slice_counter+1)*4] < max(testframe['end_tick']):
                #check in case the tempo track is longer than the notes (which happens because of stupid crap)
                high_bound = meas_ticks[(slice_counter+1)*4]
            else:
                high_bound = max(testframe['end_tick'])
                stop_early = True
        else:
            high_bound = max(testframe['end_tick'])
        #print "Starting loop.  Slice = " + str(slice_counter) + ".  Range : Tick " + str(low_bound) + " to " + str(high_bound) 

        if len(testframe[(testframe.start_tick > low_bound) & (testframe.start_tick < high_bound)]) != 0:
            #don't put anything here if the whole slice is empty or one held note            
            slice_list.append([slice_counter,testframe[(testframe.start_tick >= low_bound) & (testframe.start_tick < high_bound)]])
        
        if stop_early:
            #should only hit this condition if the tempo track is longer than the note tracks.
            break
        
        slice_counter += 1
    return slice_list


def calc_sample_stats(sample):
    this_slice = sample[1]
    st = this_slice.min(0)['start_tick']
    et = this_slice.max(0)['start_tick']
    totaldown = 0
    totalticks = (et-st)/5
    lenslice = et-st
    nonzeroticks = 0
    this_slice['Norm note'] = this_slice['note_val'] % 12

    this_slice['Nlength']=this_slice['end_tick']-this_slice['start_tick']
    ngrace = this_slice[this_slice['Nlength']<28]['Nlength'].count()

    res = this_slice.sort('start_tick')
    res['tdiff'] = res['start_tick']-res['start_tick'].shift()
    nnotelens = len(res.groupby('tdiff').start_tick.nunique())

    mc_count = 0
    mc_num = 0
    chord_list = []
    folded_chord_list = []
    old_notes = []
    this_int = []
    largestinterval = 0
    for tk in range(st,et,5):
	notes = this_slice[(this_slice.start_tick <= tk) & (this_slice.end_tick > tk)]['note_val'].ravel()
        notes.sort()
        ndown = len(notes)
        #print "tick = " + str(tk)
        #print str(ndown) + "keys down"
        totaldown += ndown
        if ndown != 0:
            nonzeroticks += 1
        if (not np.array_equal(notes,old_notes)) and (not np.array_equal(notes,np.array([]))):
            f = list(set(notes))
            f.sort()
            #print f
            if len(f)>1:
                for i in range(len(f)):
                    this_int.append(f[(i+1)%len(f)]-f[i])
                    if this_int[i] > largestinterval:
                        largestinterval = this_int[i]
		    if this_int[i]<0:
                        this_int[i] += 128
            else:
                this_int = [0]
            #print this_int
            g = [("%x" % i).zfill(2) for i in this_int]
            #print g
            h = "".join(g)
            #print h
            chord_list.append(h)
            
            mc_count += max(len(notes),len(old_notes))-len(set(notes).intersection(old_notes))
            mc_num += 1
            
            folded_notes = this_slice[(this_slice.start_tick <= tk) & (this_slice.end_tick > tk)]['Norm note'].ravel()
            folded_notes.sort()
            j = list(set(folded_notes))
            j.sort()
            k = [format(i,'x') for i in j]
            l = "".join(k)
            folded_chord_list.append(l)
        old_notes = notes
        this_int = []
        folded_notes = []
        
    cstring = " ".join(chord_list)

    if mc_num > 0:
        mc = float(mc_count)/float(mc_num)
    else:
        mc = 1
        
    if totalticks != 0:
        avedown = float(totaldown)/float(totalticks)
    else:
        avedown = 0
    if nonzeroticks != 0:
        avenonzero = float(totaldown)/float(nonzeroticks)
    else:
        avenonzero = 0
        
    fstring = " ".join(folded_chord_list)
    
    return [mc,avedown,avenonzero,cstring,fstring,lenslice,ngrace,nnotelens,largestinterval]

def build_sample_frame(filedir,process_array):
    #processing_frame = pd.DataFrame(np.array([]),columns=['Composer','Time sig num','Time sig den','Key sig','Highest note','Lowest note'])    
    for composer in os.listdir(filedir):
#    print composer
        if os.path.isdir(filedir+composer):
            for fn in os.listdir(filedir+composer+"/"):
                if os.path.isfile(filedir+composer+"/" + fn) and (fn.endswith(".mid") or fn.endswith(".MID")):
                        pattern = midi.read_midifile(filedir+composer+"/" + fn)
                        #pattern = midi.read_midifile("./Music/Bach/0778.mid")
                        print composer + "/" + fn
                        
                        slice_list = split_on_four_meas(pattern)
                        
                        for i in slice_list:
                            tf = i[1]
                            k = calc_sample_stats(i)
                            #a = to_next(tf)
                            #ngrace = np.count_nonzero(np.logical_and(a>5,a<25))
                            process_array.append([composer,max(i[1]['note_val']),min(i[1]['note_val']),fn]+k)


process_array = []
build_sample_frame(filedir,process_array)
processing_frame = pd.DataFrame(process_array,columns=['Composer','Highest note','Lowest note','Fname','Ave moving notes','Ave notes sounding', 'Ave notes no zeros','Chord string','Folded chord string', 'Ticks in slice', 'Num ornaments', 'Num note spacings','Largest interval'])


def colors(com):
    #Convert composer names to an arbitrary integer that can be used to color them in plots.
    a = pd.Series(processing_frame['Composer'].ravel()).unique()
    for i in range(len(a)):
        if a.item(i) == com:
            return i

def period(com):
    #Get stylistic period just in case we need it.
    if com in ('Bach'):
        return 'Baroque'
    elif com in ('Albeniz','Balakirew','Beethoven','Borodin','Brahms','Burgmueller','Chopin','Debussy','Godowsky','Granados','Grieg','Liszt','Mendelssohn','Moszkowski','Mussorgsky','Rachmaninov','Ravel','Schubert','Schumann','Sinding','Tchaikovsky'):
        return 'Romantic'
    elif com in ('Mozart','Haydn','Clementi'):
        return 'Classical'
    else:
        return 'Unknown'


processing_frame['Note range']=processing_frame['Highest note']-processing_frame['Lowest note']
processing_frame['To color'] = processing_frame['Composer'].apply(colors)
processing_frame['Period'] = processing_frame['Composer'].apply(period)

processing_frame.to_csv('Music_frame.csv', sep='\t')
