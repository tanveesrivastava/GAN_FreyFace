# -*- coding: utf-8 -*-
"""GAN_on_the_Frey_Face_dataset - Question 3.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1I0NxEWzamvlqTbaCFnrQb4VWNYnx0Kcd
"""

import numpy as np
import scipy.io

images = (images - 127.5) / 127.5

images = images.reshape(-1, 28, 20, 1)

import tensorflow as tf
from tensorflow.keras import layers, models, optimizers
import numpy as np
import matplotlib.pyplot as plt

def build_generator():
    model = Sequential()
    model.add(Dense(7 * 5 * 64, input_dim=100))
    model.add(Reshape((7, 5, 64)))
    model.add(Conv2DTranspose(64, kernel_size=3, strides=2, padding='same', activation='relu'))
    model.add(Conv2DTranspose(32, kernel_size=3, strides=2, padding='same', activation='relu'))
    model.add(Conv2DTranspose(1, kernel_size=3, strides=1, padding='same', activation='tanh'))
    return model

def build_discriminator():
    model = models.Sequential([
        layers.Flatten(input_shape=(28, 20, 1)),
        layers.Dense(512),
        layers.LeakyReLU(alpha=0.2),
        layers.Dense(256),
        layers.LeakyReLU(alpha=0.2),
        layers.Dense(1, activation='sigmoid')
    ])
    return model

def build_gan(generator, discriminator):
    discriminator.trainable = False
    model = Sequential()
    model.add(generator)
    model.add(discriminator)
    return model

def generator_loss(fake_output):
    return tf.reduce_mean(tf.keras.losses.binary_crossentropy(tf.ones_like(fake_output), fake_output))

def discriminator_loss(real_output, fake_output):
    real_loss = tf.keras.losses.binary_crossentropy(tf.ones_like(real_output), real_output)
    fake_loss = tf.keras.losses.binary_crossentropy(tf.zeros_like(fake_output), fake_output)
    return tf.reduce_mean(real_loss + fake_loss)

def train_gan(generator, discriminator, gan, images, epochs=100, batch_size=64):
    for epoch in range(epochs):
        idx = np.random.randint(0, images.shape[0], batch_size)
        real_images = images[idx]

        noise = np.random.normal(0, 1, (batch_size, 100))
        fake_images = generator.predict(noise)


        real_images = np.reshape(real_images, (-1, 28, 20, 1))
        fake_images = np.reshape(fake_images, (-1, 28, 20, 1))

        real_labels = np.ones((batch_size, 1))
        fake_labels = np.zeros((batch_size, 1))
        d_loss_real = discriminator.train_on_batch(real_images, real_labels)
        d_loss_fake = discriminator.train_on_batch(fake_images, fake_labels)
        d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)

        noise = np.random.normal(0, 1, (batch_size, 100))
        g_loss = gan.train_on_batch(noise, real_labels)

        print(f'Epoch {epoch + 1}/{epochs}, D Loss: {d_loss}, G Loss: {g_loss}')

def generate_faces(generator, num_samples=10):
    noise = np.random.normal(0, 1, (num_samples, 100))
    noise = np.reshape(noise, (num_samples, 100))
    generated_images = generator.predict(noise)
    generated_images = generated_images * 0.5 + 0.5
    return generated_images

data = scipy.io.loadmat('/content/frey_rawface.mat')
images = np.array(data['ff']).T.astype('float32') / 255.0

discriminator = build_discriminator()
discriminator.compile(optimizer=optimizers.Adam(lr=0.0002, beta_1=0.5), loss='binary_crossentropy')

generator = build_generator()
generator.compile(optimizer=optimizers.Adam(lr=0.0002, beta_1=0.5), loss='binary_crossentropy')

gan_input = tf.keras.Input(shape=(100,))
gan_output = discriminator(generator(gan_input))
gan = tf.keras.Model(gan_input, gan_output)
discriminator.trainable = False
gan.compile(optimizer=optimizers.Adam(lr=0.0002, beta_1=0.5), loss='binary_crossentropy')

train_gan(generator, discriminator, gan, images)

num_samples_to_generate = 10
generated_faces = generate_faces(generator, num_samples_to_generate)

import matplotlib.pyplot as plt

plt.figure(figsize=(10, 2))
for i in range(num_samples_to_generate):
    plt.subplot(1, num_samples_to_generate, i + 1)
    plt.imshow(generated_faces[i].reshape(28, 20), cmap='gray')
    plt.axis('off')
plt.show()