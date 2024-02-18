import librosa
from pyfirmata2 import Arduino, util
import time

# Define the port where your Arduino is connected
port = 'COM6'  # Change this to the appropriate port

# Create a new Arduino board instance
board = Arduino(port)

# Define pins for ULN2003 driver
activePinsS1 = [2, 3, 4, 5]  # IN1, IN2, IN3, IN4
activePinsS2 = [10, 11, 12, 13]
note_list = []
note_duration = []


# Define step sequence for the 28BYJ-48 motor
# Each element in the sequence corresponds to the coil states
# High (1) means the coil is energized, Low (0) means the coil is not energized
# The sequence is used to control the motor rotation
stepSequenceCW = [
    [1,0,0,0],  # Step 1: Coil 1 is energized
    [0,1,0,0],  # Step 2: Coil 2 is energized
    [0,0,1,0],  # Step 3: Coil 3 is energized
    [0,0,0,1]   # Step 4: Coil 4 is energized
]

stepSequenceCounterCW = [
    [0,0,0,1],   # Step 1: Coil 4 is energized
    [0,0,1,0],  # Step 1: Coil 3 is energized
    [0,1,0,0],  # Step 1: Coil 2 is energized
    [1,0,0,0]  # Step 1: Coil 1 is energized
]

# # # MY REAL CODE # # #
        
def audio_to_music(audio) :
    # Loading the audio file
    audio_file = audio
    y, sr = librosa.load(audio_file)

    # Extracting the chroma features and onsets
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr)

    first = True
    notes =[]
    
    for onset in onset_frames:
      chroma_at_onset = chroma[:, onset]
      note_pitch = chroma_at_onset.argmax()
      # For all other notes
      if not first:
          note_duration = librosa.frames_to_time(onset, sr=sr)
          notes.append((note_pitch,onset, note_duration - prev_note_duration))
          prev_note_duration = note_duration
      # For the first note
      else:
          prev_note_duration = librosa.frames_to_time(onset, sr=sr)
          first = False
    return notes

notes = audio_to_music(r"C:\Users\Joban\OneDrive - University of Waterloo\Documents\Work Files\MakeUofT2024\audio_sorohanro_-_solo-trumpet-06.wav")

for entry in notes:
    note_list.append(entry[0])
    note_duration.append(entry[2])

# Define speed (delay in seconds between steps)
delay = 60/(16*2048)

def stepperMovement1(coil_states):
    for i, state in enumerate(coil_states):
        board.digital[activePinsS1[i]].write(state)

def stepperMovement2(coil_states):
    for i, state in enumerate(coil_states):
        board.digital[activePinsS2[i]].write(state)

currentNote = 0

for j in note_list:
    # print(currentNote)
    counter = 0
    try:
        print(note_list[currentNote])
        while counter <= 3002:
            if note_list[currentNote] == 1:
                # Rotate clockwise
                for step in stepSequenceCW:
                    time.sleep(delay)
                    counter += 1
                    stepperMovement1(step)
            elif note_list[currentNote] == 3:
                # Rotate counter-clockwise
                for step in stepSequenceCounterCW:
                    time.sleep(delay)
                    counter += 1
                    stepperMovement1(step)
            elif note_list[currentNote] == 4:
                for step in stepSequenceCW:
                    time.sleep(delay)
                    counter += 1
                    stepperMovement2(step)
            elif note_list[currentNote] == 6:
                for step in stepSequenceCounterCW:
                    time.sleep(delay)
                    counter += 1
                    stepperMovement2(step)
            
        # Returns motor to original position
        while counter >= 0:
            if note_list[currentNote] == 1:
                # Rotate counter-clockwise
                for step in stepSequenceCounterCW:
                    time.sleep(delay)
                    counter -= 1
                    stepperMovement1(step)
            elif note_list[currentNote] == 3:
                # Rotate clockwise
                for step in stepSequenceCW:
                    time.sleep(delay)
                    counter -= 1
                    stepperMovement1(step)
            elif note_list[currentNote] == 4:
                for step in stepSequenceCounterCW:
                    time.sleep(delay)
                    counter -= 1
                    stepperMovement2(step)
            elif note_list[currentNote] == 6:
                for step in stepSequenceCW:
                    time.sleep(delay)
                    counter -= 1
                    stepperMovement2(step)

        currentNote += 1

    except KeyboardInterrupt:
            # Release resources
            board.exit()