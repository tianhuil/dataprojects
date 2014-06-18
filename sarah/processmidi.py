import midi
import copy
import numpy

#filename = raw_input('Enter input file: ')
filename = '0772-01.mid'

pattern = midi.read_midifile(filename)


#testing stuff to make sure I understand the format
#print pattern.format
#print pattern.resolution
#print pattern.tick_relative


#for i in range(len(pattern)):
#    for j in range(len(pattern[i])):
#        print "Track " + str(i) + ", tick " + str(j) + ": " + str(pattern[i][j])
        
#print pattern[1][10].tick
#print pattern[1][10].channel
#print pattern[1][10].data[0]
#print pattern[1][10].data[1]

#total number of ticks in the track
#t=0
#for j in range(len(pattern[1])):
#    t += pattern[1][j].tick
#
#print t

#print type(pattern[1][10])
#print isinstance(pattern[1][10], midi.events.NoteOnEvent)

#badass!  Converting each track to a list time series - [time stamp, list of notes that are "on"]

on_by_track = []
note_by_track = []
note_with_names = []

def make_tick_arrays(pat):
    #elapsed tick counter
    current_tick = 0
    
    on_at_tick = []
    on_now = []
#    on_by_track = []
    global on_by_track
    global note_by_track
    global note_with_names
    
    for i in range(len(pat)):
        for j in range(len(pat[i])):
            #just track 1 for now
            p = pat[i][j]
            if isinstance(p, midi.events.NoteOnEvent):
                if p.tick == 0 and current_tick != 0:
                #stuff is still happening on this tick.  fill the first element of the array with
                #the tick number if it hasn't already been done, then append any new notes to the "on"
                #array and remove any that are being turned off
    #                print "Staying here"
                    if p.data[1] != 0:
                        #key down event
                        on_now.append(p.data[0])
                        on_at_tick[-1][1] = copy.deepcopy(on_now)
                    else:
                        #key up event
                        on_now.remove(p.data[0])
                        on_at_tick[-1][1] = copy.deepcopy(on_now)
                        
                elif p.tick==0 and current_tick == 0:
    #                print "Initializing"
                    if p.data[1] != 0:
                        on_now.append(p.data[0])
                        
                    if not on_at_tick:
                        on_at_tick.append([0,copy.deepcopy(on_now)])
                    else:
                        on_at_tick[0][1] = copy.deepcopy(on_now)
        
                else:
    #                print "Moving forward"
                    current_tick += p.tick
                    if p.data[1] != 0:
                        #key down event
                        on_now.append(p.data[0])
                        on_at_tick.append([current_tick,copy.deepcopy(on_now)])
                    else:
                        #key up event
                        on_now.remove(p.data[0])
                        on_at_tick.append([current_tick,copy.deepcopy(on_now)])
            else:
                pass
    #           print "Not a note"
    #    print "Wrapping up track " + str(i)
        if not on_by_track:
            on_by_track = [[0,on_at_tick]]
        else:
            on_by_track.append([i,on_at_tick])
        on_now = []
        current_tick = 0
        on_at_tick = []
    #        
    #print on_at_tick
    #print on_by_track[4]
    #print bool(on_by_track[4])
    
    note_list = []
#    note_by_track = []
    for i in range(len(on_by_track)):
        if on_by_track[i]:
            for j in range(len(on_by_track[i][1])):
                if on_by_track[i][1][j][1]:
                    if note_list:
                        note_list.append(on_by_track[i][1][j][1])
                    else:
                        note_list = on_by_track[i][1][j][1]
            if note_by_track:
                note_by_track.append([i,note_list])
            else:
                note_by_track = [[i,note_list]]
            note_list = []
    
    #print note_by_track
    #print note_by_track[0][0]
    #print note_by_track[0][1]
    
    for i in range(len(note_by_track)):
        if note_by_track[i]:
            for j in range(len(note_by_track[i][1])):
                note = note_by_track[i][1][j]
                if isinstance(note,list) and len(note)==1:
                    note_by_track[i][1][j] = note[0]

    note_with_names = [None]*len(note_by_track)
#    print len(note_with_names)    
    for i in range(len(note_by_track)):
        note_with_names[i] = copy.deepcopy(note_by_track[i][1])
    
    for l in range(len(note_with_names)):
#        print note_with_names[l]
        if note_with_names[l]:
            for k in range(len(note_with_names[l])):
                if isinstance(note_with_names[l][k],int):
                    note_with_names[l][k] = midi.NOTE_NAMES[note_with_names[l][k] % midi.NOTE_PER_OCTAVE]
                else:
                    for j in range(len(note_with_names[l][k])):
                        note_with_names[l][k][j] = midi.NOTE_NAMES[note_with_names[l][k][j] % midi.NOTE_PER_OCTAVE]
    #print note_by_track

make_tick_arrays(pattern)

countnextnote = [['C',{'C':0,'Cs':0,'D':0,'Ds':0,'E':0,'F':0,'Fs':0,'G':0,'Gs':0,'A':0,'As':0,'B'
:0}],['Cs',{'C':0,'Cs':0,'D':0,'Ds':0,'E':0,'F':0,'Fs':0,'G':0,'Gs':0,'A':0,'As':0,'B'
:0}],['D',{'C':0,'Cs':0,'D':0,'Ds':0,'E':0,'F':0,'Fs':0,'G':0,'Gs':0,'A':0,'As':0,'B'
:0}],['Ds',{'C':0,'Cs':0,'D':0,'Ds':0,'E':0,'F':0,'Fs':0,'G':0,'Gs':0,'A':0,'As':0,'B'
:0}],['E',{'C':0,'Cs':0,'D':0,'Ds':0,'E':0,'F':0,'Fs':0,'G':0,'Gs':0,'A':0,'As':0,'B'
:0}],['F',{'C':0,'Cs':0,'D':0,'Ds':0,'E':0,'F':0,'Fs':0,'G':0,'Gs':0,'A':0,'As':0,'B'
:0}],['Fs',{'C':0,'Cs':0,'D':0,'Ds':0,'E':0,'F':0,'Fs':0,'G':0,'Gs':0,'A':0,'As':0,'B'
:0}],['G',{'C':0,'Cs':0,'D':0,'Ds':0,'E':0,'F':0,'Fs':0,'G':0,'Gs':0,'A':0,'As':0,'B'
:0}],['Gs',{'C':0,'Cs':0,'D':0,'Ds':0,'E':0,'F':0,'Fs':0,'G':0,'Gs':0,'A':0,'As':0,'B'
:0}],['A',{'C':0,'Cs':0,'D':0,'Ds':0,'E':0,'F':0,'Fs':0,'G':0,'Gs':0,'A':0,'As':0,'B'
:0}],['As',{'C':0,'Cs':0,'D':0,'Ds':0,'E':0,'F':0,'Fs':0,'G':0,'Gs':0,'A':0,'As':0,'B'
:0}],['B',{'C':0,'Cs':0,'D':0,'Ds':0,'E':0,'F':0,'Fs':0,'G':0,'Gs':0,'A':0,'As':0,'B'
:0}]]

def calc_transition(trk):
    #watch out - may want to add something to reset countnextnote to its old global value
    #with the zeroes if I'm ever looping over this.
    global countnextnote
    for i in range(len(midi.NOTE_NAMES)):
#        print countnextnote[i][1]['C']
    #    print countnextnote[0][1][1]
    #    print note_with_names[3]
    #    print len(note_with_names[3])
        for j in range(len(note_with_names[trk])-1):
            note = note_with_names[trk][j]
            if isinstance(note,str):
                if note==midi.NOTE_NAMES[i]:
                    #Found the note!  Increment the appropriate counter for the next one.
    #                print "Found note " + note
    #                print "Next note is " + note_with_names[trk][j+1]
                    if isinstance(note_with_names[trk][j+1],str):
                        countnextnote[i][1][note_with_names[trk][j+1]] += 1
                    else:
                        #next thing is a list - add one to everything that isn't a repeat
                        #of the current note
                        for k in note_with_names[trk][j+1]:
                            countnextnote[i][1][k] += 1
                #TODO: Handle transition from a list to another list
                
#calc_transition(4)
#print countnextnote
def construct_fake_markov(trk):
    calc_transition(trk)
    MK = numpy.matrix([[0.0]*12]*12)
    for i in range(len(midi.NOTE_NAMES)):
#        print "We're on note " + midi.NOTE_NAMES[i]
        tot_at_note = 0.0        
        for j in midi.NOTE_NAMES:
#            print "Summing: total was " + str(tot_at_note)
            tot_at_note += float(countnextnote[i][1][j])
#            print "Total is now " + str(tot_at_note)
#        print "Total number of transitions away from " + midi.NOTE_NAMES[i] + " is " + str(tot_at_note)    
        for j in range(len(midi.NOTE_NAMES)):
            if tot_at_note:
#                print "Total exists.  Dividing " + str(countnextnote[i][1][midi.NOTE_NAMES[j]]) + " by " + str(tot_at_note)
                MK[i,j] = float(countnextnote[i][1][midi.NOTE_NAMES[j]])/tot_at_note
            else:
                MK[i,j] = 0.0
    
    print MK
#    for k,v in countnextnote[i][1]

construct_fake_markov(3)                            