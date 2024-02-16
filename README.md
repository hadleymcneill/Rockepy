<p align="center">
  <img src="utilities/assets/GitHub Logo.png" width="250" height="250">
</p>



<h1 align="center">Astronaupy: User-Friendly Astrodynamics Toolkit</h1>

## Overview
Welcome to **Astronaupy** – the python astrodynamics toolkit designed with simplicity and approachability in mind. Whether you're a student taking your first steps in astronautical engineering, a researcher needing quick and reliable tools, or even an expert looking for an intuitive astrodynamics library, Astronaupy is here to guide you through the complexities of astrodynamics.

## Vision
Astronaupy aims to bridge the gap between advanced astrodynamical computations and ease of use. The core idea is to create a toolkit that "holds your hand", making it accessible to all, regardless of their prior expertise in the domain or in Python programming. The code is designed to be easy to use and easy to read, with no room for ambiguity.

## Current Development Status
Astronaupy is continuously under active development, future updates will continue to incorporate a wide range of functionalities that are both comprehensive and easy to use. I am excited about the journey ahead and am committed to continually evolving and improving. 
### Highlight Features

- **Orbital Analysis**: Users can easily configure their simulation environment with Astronaupy's **Propagation Toolkit** by including or excluding a variety of perturbations and influences, such as atmospheric drag, solar radiation pressure, and third-body effects, as well as choosing from different gravity models. This modular design allows for tailored analyses ranging from quick, high-level approximations to detailed, mission-specific simulations. Astronaupy also provides a template for users to define their own custom perturbation influences, enabling the integration of unique or mission-specific forces with ease.

- **Orbital Mechanics**: Astronaupy's **Manoeuvre Toolkit** simplifies the mission design process, enabling the planning and analysis of mission profiles with an unprecedented level of flexibility. Offering tools for advanced manoeuvre planning and trajectory optimisation with both impulse and non-impulsive methods, users can easily sequence manoeuvres one after the other to methodically build out their desired mission trajectory step-by-step, making mission design both intuitive and versatile. A template has again been provided for users to define their own custom manoeuvres for added freedom, ensuring Astronaupy caters to a broad spectrum of astrodynamics challenges.

## A brief look at whats possible with Astronaupy

#### Mission design
<p align="center">
  <img src="utilities/assets/Tutorial_1.png" width="300" height="300">
</p>

_The profile of a mission from low Earth orbit with a hohmann transfer to a geosynchronous orbit followed by a phasing manoeuvre._

---

#### Ground Track Visualisation
<p align="center">
  <img src="utilities/assets/Tutorial_2.png" width="700" height="400">
</p>

_The ground track of a satellite in a molniya orbit._

---

#### Orbit Propagation
<p align="center">
  <img src="utilities/assets/Tutorial_3.png" width="300" height="300">
</p>

_Simulation of a satellite in low Earth orbit propagated over an extended period, demonstrating how the orbit evolves due to various forces._

---

#### Low Thrust Missions
<p align="center">
  <img src="utilities/assets/Tutorial_5.png" width="300" height="300">
</p>

_Visualisation of a low thrust manoeuvre from a low to high Earth orbit._

---

#### Advanced Manoeuvres
<p align="center">
  <img src="utilities/assets/Tutorial_4.png" width="300" height="300">
</p>

_Mission simulation of an aerobraking manoeuvre to further demonstrate the capabilities of Astronaupy._

---

### Get Started with Astronaupy Tutorials
Learn how to use Astronaupy efficiently through the concise tutorials. These guides cover everything from basic setup and simple orbit calculations to more complex simulations and analyses. Perfect for users of all skill levels, they provide clear, step-by-step examples that help you quickly master the toolkit's capabilities and produce results like those above and more.  

[Explore Astronaupy Tutorials](https://github.com/hadleymcneill/Astronaupy/tree/main/tutorials)

## Planned Features
- **Intuitive Interfaces**: User-friendly functions for common astrodynamics calculations.
- **Step-by-Step Guidance**: Comprehensive documentation and examples to help users at every step.
- **Community Input**: Adapting and growing based on the feedback and needs of our user community.

## Get Involved
Head to the discussion to connect with other members of the community, I encourage you to:  
  
**Ask Questions** you’re wondering about.  
**Propose and Vote** on New Ideas for future development.  
**Share Validation Tests** to support the growth of Astronaupy.

## Installation

To install Astronaupy along with its dependencies, follow these steps:

1. **Clone the Repository**: Clone the Astronaupy repository to your local machine.

```bash
git clone https://github.com/hadleymcneill/Astronaupy.git
cd astronaupy
```

2. **Set Up  Virtual Environment** (Optional but recommended): Before installing the dependencies, it's a good idea to create a virtual environment.

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. **Install Dependencies**: Astronaupy relies on few external libraries to function correctly.

- **numpy**: Used for numerical computations.
- **scipy**: Used for optimisation.
- **pykep**: Used for the lambert solver.
- **matplotlib**: Used for visualisations.

To install these dependencies, you can use pip:

```bash
pip install numpy scipy pykep matplotlib

