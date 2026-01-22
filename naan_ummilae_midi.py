from midiutil import MIDIFile
import random

# --- CONFIGURATION ---
FILENAME = "worship_chords.mid"
TEMPO = 120
VELOCITY_STRONG = 85  # Beat 1 (The downbeat)
VELOCITY_WEAK = 70    # Beat 4 (The backbeat/pulse)
VELOCITY_BASS = 95    # Left hand strength

# --- CHORD DEFINITIONS ---
# Format: (Root relative to C, [Intervals])
# We are adding the octave (12) to the right hand for a "Fuller" sound
CHORDS = {
    'D': (2, [0, 4, 7, 12]),      # Major + Octave
    'G': (7, [0, 4, 7, 12]),
    'A': (9, [0, 4, 7, 12]),
    'Bm': (11, [0, 3, 7, 12]),    # Minor + Octave
    'Bm7': (11, [0, 3, 7, 10]),   # Minor 7
    'F#m': (6, [0, 3, 7, 12]),
    'Em': (4, [0, 3, 7, 12]),
}

# --- PROGRESSION INPUT ---
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
    ('D', 1, 6),  # D/F#
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

def add_worship_chord(track, midi, chord_name, start_time, duration, velocity):
    """
    Adds a block chord (multiple notes at once)
    """
    root_key = CHORDS[chord_name][0]
    intervals = CHORDS[chord_name][1]
    
    # Base octave for Right Hand (Middle C area)
    base_octave = 5 
    root_note = 12 * (base_octave + 1) + root_key
    
    # Play all notes in the chord simultaneously
    for interval in intervals:
        note = root_note + interval
        # Slight randomization of start time to sound human (strum effect)
        human_offset = random.uniform(0.00, 0.02) 
        midi.addNote(track, 0, note, start_time + human_offset, duration, velocity)

# --- MAIN GENERATION ---
midi = MIDIFile(1)
track = 0
time = 0
midi.addTempo(track, time, TEMPO)
midi.addTimeSignature(track, time, 6, 8, 24)

current_beat = 0

for chord_name, bars, bass_override in progression:
    
    # In 6/8 time:
    # One bar = 3 beats (quarters) or 6 eighth-notes.
    # The "Pulse" is typically on Beat 1 (0.0) and Beat 4 (1.5).
    
    clean_name = 'D' if chord_name == 'D' else chord_name
    
    for b in range(bars):
        # --- LEFT HAND (Bass) ---
        # Play once per bar, sustain for whole bar
        if bass_override is not None:
            bass_note = 36 + bass_override # F#2 range
        else:
            root_val = CHORDS[clean_name][0]
            bass_note = 36 + root_val # C2 range
            
        midi.addNote(track, 0, bass_note, current_beat, 3.0, VELOCITY_BASS)
        
        # --- RIGHT HAND (The Pulse) ---
        # Beat 1 (Strong)
        add_worship_chord(track, midi, clean_name, current_beat, 1.5, VELOCITY_STRONG)
        
        # Beat 4 (Medium - The 6/8 sway)
        # 1.5 is the midpoint of a 3.0 beat bar (representing the 4th eighth note)
        add_worship_chord(track, midi, clean_name, current_beat + 1.5, 1.5, VELOCITY_WEAK)
        
        # Advance time by 1 bar (3.0 beats)
        current_beat += 3.0

# Write File
with open(FILENAME, "wb") as output_file:
    midi.writeFile(output_file)

print(f"Successfully created {FILENAME}")
