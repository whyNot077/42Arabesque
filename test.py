from music21 import (
    stream, note, chord, tempo, meter, expressions, dynamics, instrument, volume
)
from midi2audio import FluidSynth
from pydub import AudioSegment

# Extended chord dictionary with pitches for accompaniment
chord_dict = {
    # Major chords
    "C": ["C2", "E2", "G2", "C3", "E3", "G3", "C4", "E4", "G4", "C5"],
    "C#": ["C#2", "F2", "G#2", "C#3", "F3", "G#3", "C#4", "F4", "G#4", "C#5"],
    "D": ["D2", "F#2", "A2", "D3", "F#3", "A3", "D4", "F#4", "A4", "D5"],
    "D#": ["D#2", "G2", "A#2", "D#3", "G3", "A#3", "D#4", "G4", "A#4", "D#5"],
    "E": ["E2", "G#2", "B2", "E3", "G#3", "B3", "E4", "G#4", "B4", "E5"],
    "F": ["F2", "A2", "C3", "F3", "A3", "C4", "F4", "A4", "C5", "F5"],
    "F#": ["F#2", "A#2", "C#3", "F#3", "A#3", "C#4", "F#4", "A#4", "C#5", "F#5"],
    "G": ["G2", "B2", "D3", "G3", "B3", "D4", "G4", "B4", "D5", "G5"],
    "G#": ["G#2", "C3", "D#3", "G#3", "C4", "D#4", "G#4", "C5", "D#5", "G#5"],
    "A": ["A2", "C#3", "E3", "A3", "C#4", "E4", "A4", "C#5", "E5", "A5"],
    "A#": ["A#2", "D3", "F3", "A#3", "D4", "F4", "A#4", "D5", "F5", "A#5"],
    "B": ["B2", "D#3", "F#3", "B3", "D#4", "F#4", "B4", "D#5", "F#5", "B5"],
    # Minor chords
    "Cm": ["C2", "D#2", "G2", "C3", "D#3", "G3", "C4", "D#4", "G4", "C5"],
    "C#m": ["C#2", "E2", "G#2", "C#3", "E3", "G#3", "C#4", "E4", "G#4", "C#5"],
    "Dm": ["D2", "F2", "A2", "D3", "F3", "A3", "D4", "F4", "A4", "D5"],
    "D#m": ["D#2", "F#2", "A#2", "D#3", "F#3", "A#3", "D#4", "F#4", "A#4", "D#5"],
    "Em": ["E2", "G2", "B2", "E3", "G3", "B3", "E4", "G4", "B4", "E5"],
    "Fm": ["F2", "G#2", "C3", "F3", "G#3", "C4", "F4", "G#4", "C5", "F5"],
    "F#m": ["F#2", "A2", "C#3", "F#3", "A3", "C#4", "F#4", "A4", "C#5", "F#5"],
    "Gm": ["G2", "A#2", "D3", "G3", "A#3", "D4", "G4", "A#4", "D5", "G5"],
    "G#m": ["G#2", "B2", "D#3", "G#3", "B3", "D#4", "G#4", "B4", "D#5", "G#5"],
    "Am": ["A2", "C3", "E3", "A3", "C4", "E4", "A4", "C5", "E5", "A5"],
    "A#m": ["A#2", "C#3", "F3", "A#3", "C#4", "F4", "A#4", "C#5", "F5", "A#5"],
    "Bm": ["B2", "D3", "F#3", "B3", "D4", "F#4", "B4", "D5", "F#5", "B5"],
}

def create_arabesque(input_text):
    chord_names = input_text.split()[:8]  # Use only the first 8 chords
    score = stream.Score()
    score.append(tempo.MetronomeMark(number=88))  # Tempo for the highlight section
    score.append(meter.TimeSignature('9/8'))  # Time signature remains the same

    # Melody part
    melody_part = stream.Part()
    melody_part.id = 'melody'
    melody_part.insert(0, instrument.Piano())  # Specify instrument

    # Accompaniment part
    accompaniment_part = stream.Part()
    accompaniment_part.id = 'accompaniment'
    accompaniment_part.insert(0, instrument.Piano())  # Specify instrument

    measure_length = 3  # Each measure is 3 quarter lengths in 9/8 time

    # Generate melody and accompaniment
    for i in range(42):  # 42 measures total
        chord_name = chord_names[i % len(chord_names)].strip()
        # Normalize chord name
        chord_name = chord_name.replace('♯', '#')
        if chord_name in chord_dict:
            arpeggio_notes = chord_dict[chord_name]
            num_notes = len(arpeggio_notes)

            # Accompaniment: flowing arpeggios covering multiple octaves
            for j in range(num_notes):
                n = note.Note(arpeggio_notes[j])
                n.duration.quarterLength = measure_length / num_notes  # Evenly distribute notes
                n.offset = i * measure_length + (j * n.duration.quarterLength)
                n.volume = volume.Volume(velocity=90)  # Increased volume for accompaniment
                accompaniment_part.append(n)

            # Melody: create a more expressive line
            melody_notes = []
            melody_pattern = [0, 2, 4, 6, 8, 7, 5, 3, 1]
            for k in range(len(melody_pattern)):
                idx = melody_pattern[k] % num_notes
                m = note.Note(arpeggio_notes[idx])
                m.octave += 1  # Melody is set one octave higher
                m.duration.quarterLength = measure_length / len(melody_pattern)
                m.offset = i * measure_length + (k * m.duration.quarterLength)
                m.volume = volume.Volume(velocity=110)  # Increased volume for melody
                melody_notes.append(m)

            # Add dynamics and expressions to the melody
            if i % 8 == 0:
                # Every 8 measures, add a crescendo
                cresc = dynamics.Crescendo()
                cresc.offset = melody_notes[0].offset
                melody_part.insert(cresc)
            elif i % 8 == 4:
                # At the midpoint, add a diminuendo
                dim = dynamics.Diminuendo()
                dim.offset = melody_notes[0].offset
                melody_part.insert(dim)

            for m in melody_notes:
                melody_part.append(m)
        else:
            print(f"{chord_name} not found in chord dictionary.")

    # Add parts to the score
    score.insert(0, accompaniment_part)
    score.insert(0, melody_part)
    return score

def convert_midi_to_mp3(midi_file, mp3_file, soundfont_path):
    wav_file = midi_file.replace('.mid', '.wav')
    fs = FluidSynth(soundfont_path)
    fs.midi_to_audio(midi_file, wav_file)

    sound = AudioSegment.from_wav(wav_file)
    sound.export(mp3_file, format="mp3")
    print(f"{mp3_file} has been created.")

# Updated input with a more natural chord progression
input_text = "Em D G C Am Bm Em D"

# Generate the arabesque highlight-style piece
score = create_arabesque(input_text)

# Save as MIDI file
midi_filename = "output_arabesque.mid"
score.write('midi', fp=midi_filename)

# Set SoundFont path
soundfont_path = "GeneralUser.sf2"  # Update with actual SoundFont path
mp3_filename = "output_arabesque.mp3"

# Convert MIDI to MP3
convert_midi_to_mp3(midi_filename, mp3_filename, soundfont_path)
