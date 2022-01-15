def transform(self, x, y):
    """
    Switch between 2D view and the transformed view.
    """
    # return self.transformation_in_2D(x, y)
    return self.converging_point_transformation(x, y)


def transformation_in_2D(self, x, y):
    """
    Maintain the original 2D view.
    """
    return x, y


def converging_point_transformation(self, x, y):
    """
    Give a transformed view.
    That includes new x and y values.
    """
    y_linear = y * self.converging_point_y / self.height
    if y_linear > self.converging_point_y:
        y_linear = self.converging_point_y
    x_difference = x - self.converging_point_x
    y_difference = self.converging_point_y - y_linear
    y_factor = y_difference / self.converging_point_y
    y_factor = pow(y_factor, 2)
    x_transformed = self.converging_point_x + x_difference * y_factor
    y_transformed = self.converging_point_y - y_factor * self.converging_point_y
    return x_transformed, y_transformed
