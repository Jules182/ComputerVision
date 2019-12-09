# Seam Carving

This program is intended to remove x vertical and y horizontal seams from am image.

It is an implementation of the approach by [Avidan et al., 2007](https://dl.acm.org/citation.cfm?id=1276390)

## Usage
The images to be resized must be placed in the directory ```./img/input``` and the resized versions will be placed in ```./img/output```.

Then execute the script with the parameters ```x``` and ```y``` in the following way:

```
python seamcarving.py -x {INTEGER} -y {INTEGER}
```

Argument ```x``` refers to the number of vertical seams to remove (in x direction)

Argument ```y``` refers to the number of horizontal seams to remove (in y direction)
