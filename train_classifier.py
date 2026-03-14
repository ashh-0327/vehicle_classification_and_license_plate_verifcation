import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model

DATA_PATH = 'C:\\Users\\devas\\OneDrive\\Desktop\\VehicleDetector\\dataset_vehicle'

# 1. Create a generator for TRAINING data with Data Augmentation
train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,   # Reserve 20% for validation
    rotation_range=20,      # ---  Randomly rotate images
    width_shift_range=0.2,  # ---  Randomly shift width
    height_shift_range=0.2, # ---  Randomly shift height
    shear_range=0.2,        # ---  Randomly "slant" the image
    zoom_range=0.2,         # ---  Randomly zoom in
    horizontal_flip=True,   # ---  Randomly flip images
    fill_mode='nearest'
)

# 2. Create a generator for VALIDATION data (NO augmentation!)
validation_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2      
)

# 3. Load the Training images (using the augmented generator)
train_generator = train_datagen.flow_from_directory(
    DATA_PATH,                # Folder with 'truck' and 'not_truck' subfolders
    target_size=(224, 224),
    batch_size=20,
    class_mode='binary',
    subset='training'         # use the 80% training subset
)

# 4. Load the Validation images (using the NON-augmented generator)
validation_generator = validation_datagen.flow_from_directory(
    DATA_PATH,                # Same training folder
    target_size=(224, 224),
    batch_size=20,
    class_mode='binary',
    subset='validation'       # use the 20% validation subset
)

# 5. Load the pre-trained model (MobileNetV2 is lightweight and effective)
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

# 6. Add your own Classification layer on top
x = base_model.output
x = GlobalAveragePooling2D()(x)
preds = Dense(1, activation='sigmoid')(x) # Sigmoid for Binary classification

model = Model(inputs=base_model.input, outputs=preds)

# 7. Freeze the base model layers and train only your new layer
for layer in base_model.layers:
    layer.trainable = False

# 8. Compile the model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# 9. Train the model
model.fit(
    train_generator,
    validation_data=validation_generator,
    epochs=10  
)

# 10. Save your trained model
model.save('truck_classifier_v2.h5')
print("Model trained and saved as truck_classifier_v2.h5")