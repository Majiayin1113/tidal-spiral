# FlowerV2 - Iris Generative Art

A beautiful generative art visualization that transforms the famous Iris dataset into dynamic, animated flowers using Pygame.

## Overview

FlowerV2 creates stunning flower visualizations where each Iris species is represented by a unique flower design. The petal shapes, sizes, colors, and number of petals are all derived from the actual measurements in the Iris dataset:

- **Petal Length & Width**: Control the size and shape of individual petals
- **Sepal Length & Width**: Influence the number of petals and core size
- **Species**: Determines the color palette used

## Features

✨ **Dynamic Animation**: Flowers rotate, pulse, and shimmer with life-like movement  
🌸 **Three Iris Species**: Each with distinct colors and characteristics  
🎨 **Beautiful Color Palette**: Wisteria, Ultra Violet, and Yellow Green themes  
🎮 **Interactive Controls**: Switch between species or view all at once  
📊 **Data-Driven**: Every visual element is based on actual Iris measurements  

## Installation

1. Ensure you have Python 3.10+ installed
2. Install the required packages:
   ```bash
   pip install pygame pandas
   ```

## Usage

```bash
python flowerv2.py
```

### Controls

- **1** - Show Iris-setosa (Wisteria colored)
- **2** - Show Iris-versicolor (Ultra Violet colored) 
- **3** - Show Iris-virginica (Yellow Green colored)
- **0** - Show all three species side by side
- **Esc** or **Window Close** - Exit the application

## Visualization Details

### Color Palette
- **Wisteria** (#BAACEB) - Iris-setosa
- **Ultra Violet** (#5F5AA5) - Iris-versicolor  
- **Yellow Green** (#B8D062) - Iris-virginica
- **Accent Colors**: Avocado (#5E891B) and Pakistan Green (#283B0A)

### Data Mapping
- **Petal Length** → Visual petal length (scaled by 12x)
- **Petal Width** → Visual petal width (scaled by 8x)
- **Sepal Measurements** → Number of petals and core size
- **Species Averages** → Used for consistent representation

### Animation Effects
- Gentle rotation (18°/second)
- Subtle pulsation for living effect
- Per-petal color variations for depth
- Jitter effects for organic appearance

## File Structure

```
Flower/
├── flowerv2.py          # Main application
├── Iris.csv            # Dataset (150 samples, 3 species)
└── README.md           # This file
```

## Dataset

The application uses the classic Iris dataset containing measurements for 150 iris flowers across three species:
- 50 Iris-setosa samples
- 50 Iris-versicolor samples  
- 50 Iris-virginica samples

Each sample includes:
- Sepal Length (cm)
- Sepal Width (cm)
- Petal Length (cm)
- Petal Width (cm)

## Technical Implementation

- **Graphics Engine**: Pygame for real-time rendering
- **Data Processing**: Pandas for dataset analysis
- **Animation**: Time-based transformations with sinusoidal variations
- **Rendering**: Alpha-blended surfaces with rotation transforms

## Requirements

- Python 3.10+
- pygame
- pandas
- pathlib (included in Python standard library)

## Performance

- Runs at 30 FPS
- Optimized rendering with surface rotation
- Minimal CPU usage for smooth animation

---

*This project demonstrates how data science and creative coding can combine to create beautiful, meaningful visualizations from real scientific data.*