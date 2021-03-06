import face_recognition
import click
import time
import cv2
import os

Start = time.time() # Timer Started
# This is a demo of running face recognition on live video from your webcam. The most important is, it includes some basic performance tweaks to make things run a lot faster :
#   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. Only detect faces in every other frame of video.

# Get a reference to webcam #0 (the default one), and release the variable at the end
video_capture = cv2.VideoCapture(0)

# Load a sample picture and learn how to recognize it.
# face_recognition.load_image_file(file, mode='RGB') -> Loads an image file (.jpg, .png, etc) into a numpy array

Source = os.getcwd()
Source = os.path.join(Source, "Images")
known_face_encodings = []
known_face_names = []
cnt = 0

for file in os.listdir(Source):
    print(file)
    if file.endswith((".png", ".jpg")):
        cnt += 1

        file_path = os.path.join(Source, file)
        file_image = face_recognition.load_image_file(file_path)
        
        # Create arrays of known face encodings and their names
        encodings = face_recognition.face_encodings(file_image)
        
        if len(encodings) > 1:
              click.echo("WARNING: More than one face found in the picture -> Ignoring file.".format(file))
              continue

        if len(encodings) == 0:
              click.echo("WARNING: No face was found in the picture -> Ignoring file.".format(file))
              continue
        
        known_face_encodings.append(face_recognition.face_encodings(file_image)[0])

        known_face_names.append(file[:-4])

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

End = time.time() # Timer Ended

click.echo("I/O Time (%d pics): %f sec" % (cnt, (End - Start)))

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video

        # Returns an array of bounding boxes of human faces in a image
        face_locations = face_recognition.face_locations(rgb_small_frame, model="cnn")

        # Returns a list of 128-dimensional face encodings (one for each face in the image)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations) # The second parameter is optional, means a bounding boxesof each face that we already know where it locates

        face_names = []

        for face_encoding in face_encodings:

            # See if the face is a match for the known face(s)

            # face_recognition.compare_faces(known_face_encodings, face_encoding_to_check, tolerance=0.45)
            #    1. known_face_encodings -> A list of known face encodings
            #    2. face_encoding_to_check -> A single face encoding to compare against the list
            #    3. Tolorence = 0.45 is best for predicting Asian faces (since Asian faces are all similar for the model)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.45)
            
            name = "Unknown"

            # If a match was found in known_face_encodings, just use the first one.
            if True in matches:
                # Return True value's index in match list
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

            face_names.append(name)

     # Uncoomment the code to make the video seems smoother when the person moves; while Comment it will make it faster
#    process_this_frame = not process_this_frame


    # Display the results
    # zip: https://github.com/KBLin1996/Python_Practice/edit/master/basic_python.py 
    for(top, right, bottom, left), name in zip(face_locations, face_names):

        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 2
        right *= 2
        bottom *= 2
        left *= 2

        # Draw a box around the face, color -> (B,G,R)
        # You can change color here -> if OK (green), else if Maybe (yellow), else Unknown (red)
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        # cv2.rectangle(frame, vertex's coordinate, diagonal's coordinate, line color, line breadth)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)

        # cv2.putText(frame, test, coordinate, font, size, text color, text breadth, line options (optional))
        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Face Recognition', frame)

    # Hit 'q' on the keyboard to quit !
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
