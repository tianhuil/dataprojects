import midi
import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#filename = raw_input('Enter input file: ')
filename = 'haydn-piano-sonata-31-1.mid'

pattern = midi.read_midifile(filename)


#testing stuff to make sure I understand the format
print pattern.format
print pattern.resolution
print pattern.tick_relative

#for p in pattern:
#    print pattern.index(p)

        
for i in pattern[0]:
    if isinstance(i,midi.events.KeySignatureEvent):
        ks = i.data


#for i in range(len(pattern)):
#    for j in range(len(pattern[i])):
#        print "Track " + str(i) + ", tick " + str(j) + ": " + str(pattern[i][j])
        
#print pattern[1][10].tick
#print pattern[1][10].channel
#print pattern[1][10].data[0]
#print pattern[1][10].data[1]
#print pattern

#total number of ticks in the track
t=[0]*len(pattern)
for i in range(len(pattern)):
    #tracks    
    for j in range(len(pattern[i])):
        t[i] += pattern[i][j].tick

print max(t)

#print type(pattern[1][10])
#print isinstance(pattern[1][10], midi.events.NoteOnEvent)

#badass!  Converting each track to a list time series - [time stamp, list of notes that are "on"]
#ATTN: DOES NOT WORK IF NOTES CAN BE TURNED OFF AND ON AGAIN IN THE SAME TICK.  WHICH THEY CAN.
#on_by_track = []
#note_by_track = []
#note_with_names = []
#
#def make_tick_arrays(pat):
#    #elapsed tick counter
#    current_tick = 0
#    
#    on_at_tick = []
#    on_now = []
##    on_by_track = []
#    global on_by_track
#    global note_by_track
#    global note_with_names
#    
#    for i in range(len(pat)):
#        for j in range(len(pat[i])):
#            
#            p = pat[i][j]
#            if isinstance(p, midi.events.NoteOnEvent) or isinstance(p, midi.events.NoteOffEvent):
#                if p.tick == 0 and current_tick != 0:
#                #stuff is still happening on this tick.  fill the first element of the array with
#                #the tick number if it hasn't already been done, then append any new notes to the "on"
#                #array and remove any that are being turned off
##                    print "Still on tick " + str(current_tick)
#                    if p.data[1] != 0:
#                        #key down event
#                        on_now.append(p.data[0])
#                        on_at_tick[-1][1] = copy.deepcopy(on_now)
##                        print "Added key " + str(p.data[0])
#                    else:
#                        #key up event
#                        on_now.remove(p.data[0])
#                        on_at_tick[-1][1] = copy.deepcopy(on_now)
##                        print "Removed key " + str(p.data[0])
#                        
#                elif p.tick==0 and current_tick == 0:
##                    print "Initializing"
##                    print "Track " + str(i)
##                    print "on_now list is " + str(on_now)
#                    if p.data[1] != 0:
#                        on_now.append(p.data[0])
#                        
#                    if not on_at_tick:
#                        on_at_tick.append([0,copy.deepcopy(on_now)])
#                    else:
#                        on_at_tick[0][1] = copy.deepcopy(on_now)
##                    print "First tick: " + str(on_at_tick[0][1])
#        
#                else:
##                    print "Moving forward"
#                    current_tick += p.tick
##                    print "Now on tick " + str(current_tick)
#                    if p.data[1] != 0:
#                        #key down event
#                        on_now.append(p.data[0])
#                        on_at_tick.append([current_tick,copy.deepcopy(on_now)])
##                        print "Added key " + str(p.data[0])
#                    else:
#                        #key up event
#                        on_now.remove(p.data[0])
#                        on_at_tick.append([current_tick,copy.deepcopy(on_now)])
##                        print "Removed key " + str(p.data[0])
#            else:
#                pass
#    #           print "Not a note"
##        print "Wrapping up track " + str(i)
#        if not on_by_track:
#            on_by_track = [[0,on_at_tick]]
#        else:
#            on_by_track.append([i,on_at_tick])
#        on_now = []
#        current_tick = 0
#        on_at_tick = []
#    #        
#    #print on_at_tick
##    print on_by_track[1]
#    #print bool(on_by_track[4])
#    
#    note_list = []
##    note_by_track = []
#    for i in range(len(on_by_track)):
#        if on_by_track[i]:
#            for j in range(len(on_by_track[i][1])):
#                if on_by_track[i][1][j][1]:
#                    if note_list:
#                        note_list.append(on_by_track[i][1][j][1])
#                    else:
#                        note_list = copy.deepcopy(on_by_track[i][1][j][1])
#            if note_by_track:
#                note_by_track.append([i,note_list])
#            else:
#                note_by_track = [[i,note_list]]
#            note_list = []
#    
#    #print note_by_track
#    #print note_by_track[0][0]
#    #print note_by_track[0][1]
#    
#    for i in range(len(note_by_track)):
#        if note_by_track[i]:
#            for j in range(len(note_by_track[i][1])):
#                note = note_by_track[i][1][j]
#                if isinstance(note,list) and len(note)==1:
#                    note_by_track[i][1][j] = note[0]
#
#    note_with_names = [None]*len(note_by_track)
##    print len(note_with_names)    
#    for i in range(len(note_by_track)):
#        note_with_names[i] = copy.deepcopy(note_by_track[i][1])
#    
#    for l in range(len(note_with_names)):
##        print note_with_names[l]
#        if note_with_names[l]:
#            for k in range(len(note_with_names[l])):
#                if isinstance(note_with_names[l][k],int):
#                    note_with_names[l][k] = midi.NOTE_NAMES[note_with_names[l][k] % midi.NOTE_PER_OCTAVE]
#                else:
#                    for j in range(len(note_with_names[l][k])):
#                        note_with_names[l][k][j] = midi.NOTE_NAMES[note_with_names[l][k][j] % midi.NOTE_PER_OCTAVE]
#    #print note_by_track
#
#make_tick_arrays(pattern)

#print on_by_track[1]

active_notes = {}
note_list_by_track = []
def make_note_list(pat):
    #loop over tracks.  When a note is turned on, record it in dict active_notes as a pair of
    #{value:start_tick}.  When we read a key off event for that note value, remove it from the
    #active dict, add the end tick to the list [start_tick,value,end_tick] and shove it into
    #the note list by track.
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
                if isinstance(active_notes[ev.data[0]],int):
                    #simplest case: note was turned on only once
                    tdn = active_notes[ev.data[0]]
#                    print "Removing note " + str(ev.data[0]) + " from the dict."
                    del active_notes[ev.data[0]]
                else:
                    #pain-in-the-ass case.  note was turned on twice.  take the lowest tick
                    #in the list, assign it to tdn, and get rid of it.
                    active_notes[ev.data[0]].sort()
                    tdn = active_notes[ev.data[0]].pop(0)
                    if len(active_notes[ev.data[0]])==1:
                        active_notes[ev.data[0]] = active_notes[ev.data[0]][0]
#                    else:                        
#                        active_notes[ev.data[0]] = lticks
                notes_this_track.append([tdn,note_val,tup])
            else:
                #not a note event
                pass
        note_list_by_track.append([pattern.index(p),notes_this_track])

make_note_list(pattern)
#print note_list_by_track


#tick_dict={}
ticks_collapsed = []

def collapsetracks():
    #since the notes are now in [start_tick,value,end_tick] form, this is easier.  We can
    #just concatenate the lists.
#    global tick_dict
#    for i in note_list_by_track:
#        if len(i[1])<3:
#            #skip tracks with less than 2 notes
#            pass
#        else:
#            if not tick_dict:
#                tick_dict = dict(i[1])
#            else:
#                for j in i[1]:
#                    if j[0] in tick_dict:
#                        #tick is already in the dictionary
#                        in_dict = tick_dict[j[0]]
#                        tick_dict[j[0]] = in_dict + j[1]
#                    else:
#                        tick_dict[j[0]] = j[1]
    global ticks_collapsed    
    for i in note_list_by_track:
        if len(i[1])<2:
            pass
        else:
            ticks_collapsed += i[1]
    
#collapsetracks()
#ts = np.array(ticks_collapsed)
#testframe = pd.DataFrame(ts,columns=['start_tick','note_val','end_tick'])
#print testframe[(testframe.start_tick > 4096) & (testframe.start_tick < 8192)]
#print tick_dict[16140]
#four_meas_slices = []
#print bool(four_meas_slices)
def split_on_four_meas(pattern):
#    global tick_dict
#    global four_meas_slices
    collapsetracks()
    ts = np.array(ticks_collapsed)
    testframe = pd.DataFrame(ts,columns=['start_tick','note_val','end_tick'])
    print testframe
    #--get time signature
    #--calculate how many beats 4 measures is
    #--get sorted key list for tick dictionary - ticks on which stuff happens
    #--loop through tempo track - calculate ticks that correspond to 4 measures passing, 
    #keeping in mind that the tempo is not constant
    #--return an array of dicts, split into 4-measure chunks.  DECISION: if a note
    #is held over a four-measure boundary, count it as a member of both - start
    #at the first tick in the dictionary BEFORE the boundary and end at the first tick
    #AFTER the boundary
    
    #TODO: check assumption that the tempo track is always track 0
    
    for i in pattern[0]:
        if isinstance(i,midi.events.TimeSignatureEvent):
            ts_num = i.data[0]
            ts_den = 2**(i.data[1])
    
    beats_four_meas = 4*ts_num
#    print beats_four_meas
    
    slice_counter = 0
#    ticks_in_order = sorted(tick_dict.keys)
#        if isinstance(i,midi.events.SetTempoEvent):
#            #milliseconds per quarter note
#            mpqn = i.data[0]*255**2+i.data[1]*255+i.data[2]
#            print "ms per qn: " + str(mpqn)
#            print "ticks per beat: " + str(pattern.resolution)         
#            #beats_have_passed = 
    while slice_counter*beats_four_meas*pattern.resolution < (max(t)+1):
        low_bound = slice_counter*beats_four_meas*pattern.resolution
        high_bound = (slice_counter+1)*beats_four_meas*pattern.resolution
        print "Starting loop.  Slice = " + str(slice_counter) + ".  Range : Tick " + str(low_bound) + " to " + str(high_bound) 
#        this_slice = {}
#        print "Slice dict should be empty..." + str(bool(this_slice))
#        for tk in range(slice_counter*beats_four_meas*pattern.resolution,(slice_counter+1)*beats_four_meas*pattern.resolution):
##            print "Checking tick " + str(tk)            
#            if tk in tick_dict:
##                print "Tick in dict."
#                this_slice[tk] = tick_dict[tk]
#        if four_meas_slices:
##            print "Slice array exists."
#            four_meas_slices.append([slice_counter,this_slice])
#        else:
##            print "Creating new slice array."
#            four_meas_slices = [[slice_counter,this_slice]]
        print slice_counter
        print testframe[(testframe.start_tick > low_bound) & (testframe.start_tick < high_bound)]     
        slice_counter += 1
    
    
split_on_four_meas(pattern)

#print four_meas_slices[0]
#print four_meas_slices[1]
#print four_meas_slices[2]

#ts = np.array(ticks_collapsed)
#testframe = pd.DataFrame(ts,columns=['start_tick','note_val','end_tick'])
#print testframe


#countnextnote = [['C',{'C':0,'Cs':0,'D':0,'Ds':0,'E':0,'F':0,'Fs':0,'G':0,'Gs':0,'A':0,'As':0,'B'
#:0}],['Cs',{'C':0,'Cs':0,'D':0,'Ds':0,'E':0,'F':0,'Fs':0,'G':0,'Gs':0,'A':0,'As':0,'B'
#:0}],['D',{'C':0,'Cs':0,'D':0,'Ds':0,'E':0,'F':0,'Fs':0,'G':0,'Gs':0,'A':0,'As':0,'B'
#:0}],['Ds',{'C':0,'Cs':0,'D':0,'Ds':0,'E':0,'F':0,'Fs':0,'G':0,'Gs':0,'A':0,'As':0,'B'
#:0}],['E',{'C':0,'Cs':0,'D':0,'Ds':0,'E':0,'F':0,'Fs':0,'G':0,'Gs':0,'A':0,'As':0,'B'
#:0}],['F',{'C':0,'Cs':0,'D':0,'Ds':0,'E':0,'F':0,'Fs':0,'G':0,'Gs':0,'A':0,'As':0,'B'
#:0}],['Fs',{'C':0,'Cs':0,'D':0,'Ds':0,'E':0,'F':0,'Fs':0,'G':0,'Gs':0,'A':0,'As':0,'B'
#:0}],['G',{'C':0,'Cs':0,'D':0,'Ds':0,'E':0,'F':0,'Fs':0,'G':0,'Gs':0,'A':0,'As':0,'B'
#:0}],['Gs',{'C':0,'Cs':0,'D':0,'Ds':0,'E':0,'F':0,'Fs':0,'G':0,'Gs':0,'A':0,'As':0,'B'
#:0}],['A',{'C':0,'Cs':0,'D':0,'Ds':0,'E':0,'F':0,'Fs':0,'G':0,'Gs':0,'A':0,'As':0,'B'
#:0}],['As',{'C':0,'Cs':0,'D':0,'Ds':0,'E':0,'F':0,'Fs':0,'G':0,'Gs':0,'A':0,'As':0,'B'
#:0}],['B',{'C':0,'Cs':0,'D':0,'Ds':0,'E':0,'F':0,'Fs':0,'G':0,'Gs':0,'A':0,'As':0,'B'
#:0}]]
#
#def calc_transition(trk):
#    #watch out - may want to add something to reset countnextnote to its old global value
#    #with the zeroes if I'm ever looping over this.
#    global countnextnote
#    for i in range(len(midi.NOTE_NAMES)):
##        print countnextnote[i][1]['C']
#    #    print countnextnote[0][1][1]
#    #    print note_with_names[3]
#    #    print len(note_with_names[3])
#        for j in range(len(note_with_names[trk])-1):
#            note = note_with_names[trk][j]
#            if isinstance(note,str):
#                if note==midi.NOTE_NAMES[i]:
#                    #Found the note!  Increment the appropriate counter for the next one.
#    #                print "Found note " + note
#    #                print "Next note is " + note_with_names[trk][j+1]
#                    if isinstance(note_with_names[trk][j+1],str):
#                        countnextnote[i][1][note_with_names[trk][j+1]] += 1
#                    else:
#                        #next thing is a list - add one to everything that isn't a repeat
#                        #of the current note
#                        for k in note_with_names[trk][j+1]:
#                            countnextnote[i][1][k] += 1
#                #TODO: Handle transition from a list to another list
#                
##calc_transition(4)
##print countnextnote
#def construct_fake_markov(trk):
#    calc_transition(trk)
#    MK = np.matrix([[0.0]*12]*12)
#    for i in range(len(midi.NOTE_NAMES)):
##        print "We're on note " + midi.NOTE_NAMES[i]
#        tot_at_note = 0.0        
#        for j in midi.NOTE_NAMES:
##            print "Summing: total was " + str(tot_at_note)
#            tot_at_note += float(countnextnote[i][1][j])
##            print "Total is now " + str(tot_at_note)
##        print "Total number of transitions away from " + midi.NOTE_NAMES[i] + " is " + str(tot_at_note)    
#        for j in range(len(midi.NOTE_NAMES)):
#            if tot_at_note:
##                print "Total exists.  Dividing " + str(countnextnote[i][1][midi.NOTE_NAMES[j]]) + " by " + str(tot_at_note)
#                MK[i,j] = float(countnextnote[i][1][midi.NOTE_NAMES[j]])/tot_at_note
#            else:
#                MK[i,j] = 0.0
#    
#    print MK
#
#
##construct_fake_markov(3)                                