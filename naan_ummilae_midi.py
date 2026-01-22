from midiutil import MIDIFile
import random

# --- CONFIGURATION ---
FILENAME = "worship_piano_6_8.mid"
TEMPO = 120  # BPM (In 6/8 at 120, these 8th notes will flow quickly. Adjust in DAW if needed)
VELOCITY_STRONG = 85
VELOCITY_WEAK = 65
VELOCITY_BASS = 90

# --- CHORD DEFINITIONS ---
# Format: (Root relative to C, [Intervals])
# C=0, C#=1, D=2...
CHORDS = {
    'D': (2, [0, 4, 7]),
    'G': (7, [0, 4, 7]),
    'A': (9, [0, 4, 7]),
    'Bm': (11, [0, 3, 7]),
    'Bm7': (11, [0, 3, 7, 10]),
    'F#m': (6, [0, 3, 7]),
    'Em': (4, [0, 3, 7]),
}

# --- PROGRESSION INPUT ---
# (Chord Name, Bars, Bass Note Override)
# Bass Note Override: None = Root. Integer = MIDI note offset (relative to C)
progression = [
    ('Bm7', 2, None),
    ('G', 2, None),
    ('A', 2, None),
    ('F#m', 2, None),
    ('Bm7', 2, None),
    ('G', 2, None),
    ('A', 2, None),
    ('F#m', 1, None),
    ('A', 1, None),
    ('D', 1, None),
    ('D', 1, 6),  # D/F# (F# bass)
    ('G', 2, None),
    ('Em', 1, None),
    ('A', 1, None),
    ('D', 1, None),
    ('Bm', 1, None),
    ('D', 2, None),
    ('G', 2, None),
    ('Em', 1, None),
    ('A', 1, None),
    ('D', 2, None)
]

def get_midi_note(chord_name, octave):
    root_base = 12 * (octave + 1) # C1 = 24
    if chord_name not in CHORDS:
        return 60 # Default to middle C if error
    root_offset = CHORDS[chord_name][0]
    return root_base + root_offset

def create_arpeggio_pattern(chord_name, bars, start_time, track, midi):
    """
    Creates a 6/8 worship pattern: Root-5-8-9-8-5 (or similar)
    In MIDIUtil (and standard MIDI), 1 beat = Quarter Note.
    In 6/8, one bar = 3 "Quarter Note" beats (6 eighth notes).
    Eighth note duration = 0.5
    """
    
    root_key = CHORDS[chord_name][0]
    intervals = CHORDS[chord_name][1]
    
    # Base MIDI notes for this chord (Middle C octave)
    # We construct a pool of notes: Root, 3rd, 5th, Octave, 9th
    base_octave = 5 # Octave 5
    root_note = 12 * (base_octave + 1) + root_key
    
    # Notes for arpeggio (Root, 5th, Octave, 3rd)
    # Pattern: Low(1) - Mid(5) - High(1) - Mid(3) - High(5) - Mid(3)
    # Adjusting to generic intervals
    p_1 = root_note # Root
    p_3 = root_note + intervals[1] # 3rd
    p_5 = root_note + intervals[2] # 5th
    p_8 = root_note + 12 # Octave
    
    # 6/8 Pattern sequence (6 notes per bar)
    # A standard flowing worship pattern
    pattern_notes = [p_1, p_5, p_8, p_3, p_5, p_3]
    
    # Calculate duration in MIDI beats
    # 1 Bar of 6/8 = 6 eighth notes. Each eighth note is 0.5 beats.
    # Total bar duration = 3.0 beats.
    
    current_time = start_time
    
    for b in range(bars):
        # --- LEFT HAND (Bass) ---
        # Play on beat 1, hold for full bar
        bass_note_val = root_note - 24 # 2 octaves down
        
        # Handle Slash Chords (e.g. D/F#)
        # We look up the specific override from the progression list logic passed earlier? 
        # For simplicity here, we assume standard root unless modified in main loop.
        # (See main loop for Bass Override application)
        
        # We will write the Bass note in the main loop to handle overrides easier.
        # This function handles the Right Hand Arpeggios.
        
        # --- RIGHT HAND (Arpeggio) ---
        for i, note in enumerate(pattern_notes):
            # Humanize Velocity
            if i == 0:
                vel = VELOCITY_STRONG # Downbeat
            elif i == 3:
                vel = VELOCITY_STRONG - 5 # Secondary strong beat (beat 4 of 6)
            else:
                vel = VELOCITY_WEAK + random.randint(-5, 5)
            
            # Add note
            midi.addNote(track, 0, note, current_time, 0.5, vel)
            current_time += 0.5
            
    return current_time

# --- MAIN GENERATION ---
midi = MIDIFile(1)
track = 0
time = 0
midi.addTempo(track, time, TEMPO)
midi.addTimeSignature(track, time, 6, 8, 24) # 6/8 Time

current_beat = 0

for chord_name, bars, bass_override in progression:
    
    # 1. Add Bass Note (Left Hand)
    # Calculate duration: 3.0 beats per bar (6 * 0.5)
    duration = bars * 3.0
    
    if bass_override is not None:
        # Custom Bass (e.g. F# is 6)
        # Map to octave 3 (approx MIDI 42-53)
        bass_note = 36 + bass_override # F#2 range
    else:
        # Standard Root
        root_val = CHORDS[chord_name][0]
        bass_note = 36 + root_val # C2 range
        
    midi.addNote(track, 0, bass_note, current_beat, duration, VELOCITY_BASS)
    
    # 2. Add Arpeggios (Right Hand)
    # Note: We pass control to function, but we need to handle the D/F# special case for RH too?
    # Actually D/F# RH is just D major. The function handles D Major fine.
    
    # D/F# special handling for variable names if needed
    clean_name = 'D' if chord_name == 'D' else chord_name
    
    create_arpeggio_pattern(clean_name, bars, current_beat, track, midi)
    
    current_beat += duration

# Write File
with open(FILENAME, "wb") as output_file:
    midi.writeFile(output_file)

print(f"Successfully created {FILENAME}")
