from manimlib.imports import *

#Helper Function that helps get the vector field for a certian ammount of point particles
def get_force_field_func(*point_strength_pairs, **kwargs):
    radius = kwargs.get("radius", 0.5)

    def func(point):
        result = np.array(ORIGIN)
        for center, strength in point_strength_pairs:
            to_center = center - point
            norm = get_norm(to_center)
            if norm == 0:
                continue
            elif norm < radius:
                to_center /= radius**3
            elif norm >= radius:
                to_center /= norm**3
            to_center *= -strength
            result += to_center
        return result
    return func

#Defining an electric particle class that can have a default size 
class ElectricParticle(VectorizedPoint):
    CONFIG = {
        "radius": 0,
        "color": WHITE
    }
    def __init__(self,**kwargs):
        digest_config(self, kwargs)
        super().__init__()
        circle = Circle(radius = self.radius, fill_opacity = 1.0, color = self.color)
        circle.move_to(self)
        self.add(circle)


class ChangingElectricField(MovingCameraScene):
    CONFIG = {
        "vector_field_config": {},
        "start_line_y": 0.5,
        "end_line_y": 3,
        "anim_time": 10,
        "displacements_to_test":[3,2.5,0.5, 0.1, 0.01],
        "displacement_animation_times": [15,15,10,5,5],
        "x_axis_length": 10,
        "y_axis_length": 2,
        "stroke_width": .05,
        "init_number_points": 6,
        "animation_iterations":3,
        "total_charge": 5,
        "test_charge_magnetude": 0.5,
        "test_charge_mass": 1,
        "test_charge_radius": .0025,
        "test_charge_init_displacement": 3,
        "test_charge_color": GREEN,
        "wait_time": 2,
        "initial_pvt_axes_config" : {
            "x_min" : 0,
            "x_max" : 15,
            "x_axis_config" : {
                "unit_size" : 10/15,
                "numbers_to_show" : list(range(1, 15)),
            },
            "y_min" : -3,
            "y_max" : 3,
            "y_axis_config" : {
                "unit_size" : .3,
                "tick_frequency" : 3,
                "label_direction" : LEFT,
                "numbers_to_show": [-3,3],
                
            },
        },
        "text_scale_val": 0.75,
        "time_label": 5,
        "pos_label": 2,
        "screen_ratio_for_graph": 1.0/3.0,
        "aspect_ratio": 16.0/9.0
        }
    

    #We actually animate using this method
    def construct(self):
        self.set_up_particles_and_v_field()  #1
        self.show_particles_and_field()
        self.wait()   #2
        self.refine_particles_and_field()   #3
        self.rollIntro()
 
        for i in range(0, len(self.displacements_to_test)):
            self.play(FadeIn(self.set_up_axes(
                x_max = self.displacement_animation_times[i],
                x_min = 0, 
                x_axis_config={"unit_size": self.x_axis_length/self.displacement_animation_times[i], "numbers_to_show": list(range(1,self.displacement_animation_times[i]))},
                y_min = -1.1*self.displacements_to_test[i],
                y_max = 1.1*self.displacements_to_test[i],
                y_axis_config = {"unit_size": self.y_axis_length/ self.displacements_to_test[i], "decimal_number_config": {"num_decimal_places": int(-np.log10(self.displacements_to_test[i]))}, "label_direction":UP, "include_numbers": True, "tick_frequency":self.displacements_to_test[i], "numbers_to_show":[-self.displacements_to_test[i],self.displacements_to_test[i]]}
                ) ) )
            self.set_up_test_charge(self.displacements_to_test[i])
            self.zoom_to_charge(self.displacements_to_test[i])
            self.play(FadeIn(self.test_charge), ShowCreation(self.bracket_group))
            self.wait()
            self.play(Write(self.set_up_text_label(self.displacements_to_test[i],self.displacement_animation_times[i])))
            self.draw_theoretical_SHM_Graph(self.displacements_to_test[i], self.displacement_animation_times[i])
            self.wait()
            self.play(FadeOut(self.bracket_group))
            self.trace_point()
            self.play_test_charge(self.displacement_animation_times[i])
            self.play(FadeOut(self.test_charge), FadeOut(self.trace_group),FadeOut(self.graph_and_BR), FadeOut(self.theo_g), FadeOut(self.text), FadeOut(self.theo_g_label))

    # #This function rolls the introduction and background information    
    def rollIntro(self):
        #setting up number plane and labels
        plane = NumberPlane()
        label_a = TexMobject("a", color = RED).next_to(np.array([0,self.start_line_y,0]), RIGHT, buff = MED_SMALL_BUFF)
        label_b = TexMobject("b", color = YELLOW).next_to(np.array([0,self.end_line_y,0]), RIGHT, buff = MED_SMALL_BUFF)
        label_neg_a = TexMobject("-a", color = RED).next_to(np.array([0,-self.start_line_y,0]), RIGHT, buff = MED_SMALL_BUFF) 
        label_neg_b = TexMobject("-b", color = YELLOW).next_to(np.array([0,-self.end_line_y,0]), RIGHT, buff = MED_SMALL_BUFF)
        labels_side = VGroup(label_a, label_b, label_neg_a, label_neg_b)
        for label in labels_side:
            label.scale(0.7)
        #setting up Tex and formulas
        e_field_text = TexMobject(r"\textup{If the linear charge densities on the rods} \\ \textup{are positive, uniform and given by } \lambda \textup{,} \\ \textup{then the Electric Field Vector}\\ \textup{at any point along the} x \textup{ axis is given by:}", color = BLUE_A, tex_to_color_map = {r"\lambda": WHITE})
        e_field_text.scale(0.75)
        e_field_tex = TexMobject(r"\mathbf{E} = \frac{\lambda }{4\pi \epsilon _{0}}(\frac{2b}{\sqrt{x^{2}+b^{2}}} - \frac{2a}{\sqrt{x^{2}+a^{2}}})i\hat{}", color  = BLUE_A,)
        e_field_tex.next_to(e_field_text, DOWN, buff = MED_LARGE_BUFF)
        efield = VGroup(e_field_text, e_field_tex)
        efield.shift(3*UP+3.2*LEFT)
        efield.scale(0.75)

        #setting up SHM TEx and information
        shm_text = TexMobject(r"\textup{For Smaller and Smaller values of } x \textup{,} \\ \textup{a small test charge of charge }-Q \textup{ and mass }m \\ \textup {executes simple harmonic motion with frequency } \omega", color = BLUE_A, tex_to_color_map ={"-\Q": GREEN, r"\omega": PURPLE})
        shm_text.scale(0.75)
        shm_tex = TexMobject(r"\omega = \sqrt{\frac{\lambda Q(b^{2}-a^{2})}{4\pi \epsilon _{0}a^{2}b^{2}}}", color = BLUE_A , tex_to_color_map = {r"\omega": PURPLE})
        shm_tex.next_to(shm_text, DOWN, buff = MED_LARGE_BUFF)
        shm = VGroup(shm_text, shm_tex)
        shm.shift(1.5*DOWN,3.2*RIGHT)
        shm.scale(0.75)
        #displaying and animating stuff
        self.play(FadeOut(self.vector_field), ShowCreation(plane), Write(labels_side))
        self.wait()
        self.play(Write(efield), run_time = 5)
        self.wait(5)
        self.play(Write(shm), run_time = 5)
        self.wait(5)
        self.play(FadeOut(shm), FadeOut(efield), FadeOut(plane), FadeIn(self.vector_field))

    #Shows the particles and field initially, one by 1 
    def show_particles_and_field(self):
        self.play(
            *list(map(ShowCreation, self.vector_field)),
            *list(map(GrowFromCenter, self.particles))
        ) 

    #Draws the theoretical SHM Plot, x_width is the amplitude
    def draw_theoretical_SHM_Graph(self, x_width, time):
        angular_frequency = np.sqrt((self.test_charge_magnetude*self.total_charge*(self.end_line_y+self.start_line_y))/(self.start_line_y**2 * self.end_line_y**2 * self.test_charge_mass)) #calculating the angular frequency
        theo_g = self.p_v_t_axes.get_graph(lambda x: x_width*np.cos(angular_frequency*x), color = PURPLE) #making the graph itself
        theo_g_label = TexMobject("x(t) = \\Delta x \\cos(\\omega t)", color = PURPLE) #Label for the graph
        theo_g_label.scale(.75* self.camera.get_frame_width()/FRAME_WIDTH) #Scaling the width
        theo_g_label.next_to(self.p_v_t_axes.coords_to_point(time, -3*x_width/4), buff = x_width/100) #moving the label
        self.theo_g = theo_g # setting the graph as an instance variable removed it later
        self.theo_g_label = theo_g_label #setting the label as an instance variable so we can remove it later
        self.p_v_t_axes.add(theo_g)
        self.add_foreground_mobject(theo_g_label)
        self.play(ShowCreation(self.theo_g), Write(theo_g_label)) # animating the graph and the label

    #setting up the test charge based on the x_width of the scene
    def set_up_test_charge(self,x_width):
        test_charge = ElectricParticle(radius = x_width/40, color = self.test_charge_color) #Defining the charge
        test_charge.charge = -self.test_charge_magnetude #setting the magnetude of the test charge
        test_charge.velocity = 0 #starts at 0 velocity
        test_charge.move_to(np.array([x_width,0,0]))
        #making the measure line that displays the delta x along with the label
        measure_line = Line(ORIGIN, np.array([FRAME_WIDTH/2,0,0]), color = self.test_charge_color)
        label = TexMobject("\\Delta x ="+str(x_width), color = self.test_charge_color)
        label.scale(0.75)
        label.move_to(np.array([x_width/2, measure_line.get_center()[1] - label.get_height(),0]))
        self.bracket_group = VGroup(measure_line, label)
        self.bracket_group.scale(2*x_width/FRAME_WIDTH, about_point = ORIGIN)
        label.move_to(measure_line.get_center()-np.array([0, test_charge.radius+label.get_height(),0]))
        self.bracket_group.shift(np.array([0,-1.2*test_charge.radius,0])) #setting the v group as an instance variable
        self.test_charge = test_charge #Setting test charge as an the instance variable so we can remove it later on
    
    #Begins animating the test charge and adds the updater
    def play_test_charge(self, wait_time):
        def update_test_charge(test_charge,dt): #define the update function based on coloumbs law and newtons 2nd law
            func = get_force_field_func(*list(zip(
            list(map(lambda x: x.get_center(), self.particles)),
            [p.charge for p in self.particles])))
            force = func(test_charge.get_center()) * test_charge.charge
            test_charge.velocity += (force/self.test_charge_mass)*dt 
            test_charge.shift(test_charge.velocity*dt)
        
        
        self.test_charge.add_updater(update_test_charge) # adding the updater to the test charge
        self.wait(wait_time) #Wait in order for the charge to do its thing

    #Helps set up the test labels that indicate the values of delta x and L
    def set_up_text_label(self, x_width, time):
        rod_label = TexMobject("L_{Rods} = "+ str(self.end_line_y - self.start_line_y), color = WHITE)
        test_label = TexMobject("\\Delta x = " + str(x_width), color=self.test_charge_color)
        fraction_label = TexMobject(r"\frac{\Delta x}{L} =" + str(x_width/(self.end_line_y - self.start_line_y))+ r", \ \ \frac{\Delta x^{2}}{L^{2}} = "+ str((x_width**2)/((self.end_line_y - self.start_line_y)**2)))
        test_label.next_to(rod_label, DOWN, buff = SMALL_BUFF)
        text_group = VGroup(rod_label, test_label)
        self.text = text_group
        text_group.move_to(self.p_v_t_axes.coords_to_point(time*1.4, x_width*0.75))
        fraction_label.next_to(test_label, DOWN, buff = SMALL_BUFF)
        text_group.scale(0.75*self.camera.get_frame_width()/FRAME_WIDTH)
        fraction_label.scale(0.75*self.camera.get_frame_width()/FRAME_WIDTH)
        self.add_foreground_mobject(self.text)
        return text_group

    #setting up the initial particles and electric vector field
    def set_up_particles_and_v_field(self):
        #The electric particles that make up the line, getting the inital number 
        particles = self.get_particles(2)
        self.particles = particles
        #initializing the vector field and assigning it as an instance variable
        vector_field = self.get_vector_field(self.particles)
        self.vector_field = vector_field
        self.add_foreground_mobject(self.particles)

    #this is the function that refines the particles and increases the approximation in order to better approximate a rod
    def refine_particles_and_field(self):
        self.wait(self.wait_time)
        count = 1 # number of previous animations
        while(count<=self.animation_iterations):
            particles_temp = self.get_particles(self.init_number_points**(count)) #the number of particles goes up exponentially each time so it can better approximate a rod
            new_field = self.get_vector_field(particles_temp) #the new field is generated based on the new particles coming up
            #Bringing the particles to the foreground and vector field to the background
            self.add_foreground_mobject(particles_temp)
           
            
            #transitioning to the new stuff
            self.play(
            AnimationGroup(FadeOut(self.particles), *list(map(GrowFromCenter, particles_temp))),
            FadeOut(self.vector_field), FadeIn(new_field)
            )
            # editing the vector field and the particles

            self.particles = particles_temp
            self.vector_field = new_field
            self.wait(self.wait_time)
            count+=1 # increasing count of animations
    
    # This is the function that will generate an approximation of the rod given a number of particles
    def get_particles(self, number_points):
        particles =  VGroup()
        length = self.end_line_y - self.start_line_y
        #calulating how long each partition of the line is
        length_partition = length / (number_points - 1)
        #calculating the increment of the loop
        #Add the restriction that the radius of each point also equals the stroke width of the lines
        radius_point = self.stroke_width
        #in order to calculate the radius of the point we use the formula
        for i in range(0, number_points):
            particle = ElectricParticle(radius = radius_point)
            particle.charge = self.total_charge/number_points
            particles.add(particle)
            particle.move_to(np.array([0, self.end_line_y-(length_partition*i),0]))
        for i in range(0, number_points):
            particle = ElectricParticle(radius = radius_point)
            particle.charge = self.total_charge/number_points
            particle.move_to(np.array([0, -self.end_line_y+(length_partition*i),0]))
            particles.add(particle)

        return particles

    # Makes the vector field based on the ammount of particles
    def get_vector_field(self, particle_set):
        func = get_force_field_func(*list(zip(
            list(map(lambda x: x.get_center(), particle_set)),
            [p.charge for p in particle_set]
        )))
        vector_field = VectorField(func, **self.vector_field_config)
        return vector_field

    # This is the function that traces the points motion onto the graph
    def trace_point(self):
        tracer = Circle(radius=self.test_charge.radius/3, color = self.test_charge_color, fill_opacity = 1) #making the actual circle that traces
        tracer.move_to(self.p_v_t_axes.coords_to_point(0,self.test_charge.get_center()[0])) # The x coordinate is where it starts
        #making the path, with two points
        path = VMobject(color = self.test_charge_color)
        path.set_points_as_corners([tracer.get_center(),tracer.get_center()+0.00001*DOWN])
        group = VGroup(path, tracer)
        self.play(FadeIn(group))
        self.trace_group = group
        #Path updater
        def trace_and_update(group,dt):
            tracer_cen = self.p_v_t_axes.point_to_coords(tracer.get_center())
            tracer.move_to(self.p_v_t_axes.coords_to_point(tracer_cen[0]+dt,self.test_charge.get_center()[0]))
            temp_path = path.copy()
            temp_path.append_vectorized_mobject(Line(temp_path.points[-1], tracer.get_center(), color = self.test_charge_color))
            temp_path.make_smooth()
            path.become(temp_path)
        
        self.p_v_t_axes.add(path)
        group.add_updater(trace_and_update)
        
        
    
    #Sets up the axes and frames for each cycle
    def set_up_axes(self, **kwargs):
        #Defining a frame
        frame = ScreenRectangle(aspect_ratio= self.aspect_ratio/self.screen_ratio_for_graph, fill_color = self.camera.background_color, fill_opacity = 1.0)
        frame.set_width(self.camera.get_frame_width())
        frame.move_to(np.array([0,self.camera.get_frame_height()/2*(1-self.screen_ratio_for_graph),0])+self.camera.get_frame_center())
        self.frame=frame
        #defining the position versus time axes
        config = dict(self.initial_pvt_axes_config)
        config.update(kwargs)
        p_v_t_axes = Axes(**kwargs)
        p_v_t_axes.x_axis.add_numbers()
        p_label = TextMobject("x-Position")
        t_label = TextMobject("Time")
        labels = VGroup(p_label, t_label)
        for label in labels:
            label.scale(self.text_scale_val)
        t_label.next_to(
            p_v_t_axes.x_axis.get_right(),
            RIGHT, buff = SMALL_BUFF
        )
        p_label.next_to(
            p_v_t_axes.y_axis.get_top(),
            UP, buff = SMALL_BUFF
        )
        
        p_v_t_axes.add(labels)
        #scaling the axes acoording to the camera width
        p_v_t_axes.scale(0.50 * self.camera.get_frame_width()/FRAME_WIDTH)
        p_v_t_axes.move_to(frame.get_center() - (p_v_t_axes.get_center() - p_v_t_axes.coords_to_point(p_v_t_axes.x_max / 2,0)))
        self.p_v_t_axes = p_v_t_axes
        self.graph_and_BR = VGroup(frame, p_v_t_axes)
        self.add_foreground_mobject(self.graph_and_BR)
        return self.graph_and_BR

    
    #The function that zooms to the charge in question, it keeps the position of the frame constant as well.
    def zoom_to_charge(self, x_width):
        center_point = np.array([0,(self.screen_ratio_for_graph*x_width/self.aspect_ratio),0])
        graph_move_point = np.array([0,1.2*x_width/self.aspect_ratio * (1-self.screen_ratio_for_graph),0])+center_point# +(np.array([0,self.camera.get_frame_height()/2*(1-self.screen_ratio_for_graph),0])-self.frame.get_center())
       
        self.play(
        self.camera_frame.set_width, 2.4*x_width, 
        self.camera_frame.move_to,center_point,
        self.graph_and_BR.set_width,x_width*2.4,
        self.graph_and_BR.move_to, graph_move_point
        )
        self.wait(0.5)

