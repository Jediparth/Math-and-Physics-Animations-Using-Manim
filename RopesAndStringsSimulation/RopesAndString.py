#This is file makes a rope Mobject that can emulate most any string. The rope will be composed of many discrete nodes with mass that are pull on each other 
from big_ol_pile_of_manim_imports import *
#from manimlib.imports import *

#helper functions
#THIS IS STILL A WORK IN PROGRESS

#Perhaps move everything perpendicularly? Edit apply_force func
class Rope(VGroup):
    CONFIG = {
        "color": WHITE,
        "linear_mass_density": lambda x: 10, #linear_mass_density = mass of node / segment_length = total_mass/length = number_nodes*mass_of_node/length => segment_length = length/number_nodes
        "length": 8,
        "number_nodes": 100,
        "thickness": 0.05,
        "start": LEFT*4,
        "spring_k":2500,
        "orientation": RIGHT,
        "frequency": 5/16 * np.sqrt(20),
        "amplitude": 0.75,
        "tension": 200,
        "cycles":7,
        "dampening_constant": 0, #TODO
        "right_end_fixed": True,
        "left_end_fixed": True,
        "strumming": False,
        "rope_length_to_strum": 5, 
        "time_to_strum": 5, #seconds
        "length_to_strum": 1.5,
        "lengths_to_hold": [16/3, 1],
        "time_to_hold": 3,
        "hold_indefinetly": False,
        "smooth": False,
        "net_force": np.array([0,0,0]), #A net forc on ALL Nodes that ARENT fixd
        "lengths_to_put_force_on": [], #The lengths to put the forces on
        "forces_on_lengths": [],
        "opacity": 1.0,
        "harmonic": 1,
        "set_manually": True
    }
    def __init__(self, **kwargs):
        #initializing the v group itself and other important arrays
        VGroup.__init__(self)
        digest_config(self, kwargs)
        #initializing the arrays with the forces
        self.dampening_force = np.zeros((self.number_nodes,3))
        self.spring_force = np.zeros((self.number_nodes,3))
        #initializing the timer 
        self.time = 0  #this is the timer
        #Setting frequency perhaps
        if(not self.set_manually):
            self.set_frequency()
        #Calculating constants based on config dict
        self.length_between_centers = self.length/self.number_nodes
        self.spring_eq_length = self.length_between_centers - (self.tension/self.spring_k)
        
        #Making the arrays that represent position velocity and the mass of each node
        self.masses = np.zeros(self.number_nodes) #Array of masses
        self.v = np.zeros((self.number_nodes,3)) #Array of velocities of each node
        self.x = np.zeros((self.number_nodes,3)) #Array of positions of each node

        #Calculating which node to pluck and which ones to hold and apply net force to
        self.node_to_strum = self.length_to_node(self.rope_length_to_strum)
        self.nodes_to_hold = self.generate_nodes_from_length(self.lengths_to_hold)
        self.nodes_with_net_force = self.generate_nodes_from_length(self.lengths_to_put_force_on)
        
        #setting up the initial positions and masses of the nodes
        for i in range(0, self.number_nodes):
            length = self.length_between_centers*i
            self.x[i] = length*self.orientation + self.start
            self.masses[i] = self.linear_mass_density(length)*self.length_between_centers
        
        self.set_up_nodes() #Adding the nodes
        self.add_connecting_lines() #Adding the lines
    
    #Sets the frequency to the harmonic specified
    def set_frequency(self):
        if(self.left_end_fixed == self.right_end_fixed): #We have to assign values to frequency based on the boundary conditions
            self.frequency = self.harmonic * self.get_fundemental_freq(True)
            self.wavelength = 2*self.length/self.harmonic
        else:
            self.frequency = self.harmonic * self.get_fundemental_freq(False)
            self.wavelength = 4*self.length/self.harmonic

    #This function, moves each node, (Either a circle or vectorized pt) to its respective location
    def set_up_nodes(self):
        #Adds either a Vpoint or Circle at that location, adding it to the self v group
        for i in range(0,self.number_nodes):
            if (self.smooth):
                self.add(VectorizedPoint(self.x[i]))
            else:
                circ = Circle(color = self.color, stroke_opacity = self.opacity, fill_opacity = self.opacity , radius = self.thickness/2)
                circ.move_to(self.x[i])
                self.add(circ)
    
    #The displacement function of time that we generated in the config
    def displacement_function(self, t):
        return self.amplitude*np.sin(2*PI*self.frequency*t) #-> simply in the form y=Asin(2pi*ft)
    
    #This is the derivative of the diplacement function to set the velocity in order to be consistent
    def velocity_function(self, t):
        return self.amplitude*2*PI*self.frequency*np.cos(2*PI*self.frequency*t)
    
    #this function returns the spring force between on a node at point xi where the other node is at point xj
    def get_spring_force(self, xi, xj):
        s = xi -xj
        if(np.linalg.norm(s) == self.spring_eq_length): #stops any invalid values
            return np.array([0,0,0])
        s_hat = s/np.linalg.norm(s)
        return -self.spring_k*(np.linalg.norm(s)-self.spring_eq_length)*s_hat 
    
    #This returns the dampening force on a node with velocity vi
    def get_dampening_force(self, vi):
        return -self.dampening_constant*vi

    
    #This converts a length along the rope to a node that can be given commands
    def length_to_node(self,length): 
        val = int(length//self.length_between_centers)
        return val

    #This generates the nodes to hold from the list of lengths_to_hold specified in config
    def generate_nodes_from_length(self, lengths):
        nodes = []
        for i in range(0, len(lengths)):
            nodes.append(self.length_to_node(lengths[i]))
        return nodes
    
    #adds updaters depending on whether the rope is being strummed or not
    def updater_adder(self):
        self.clear_updaters()
        if(self.strumming):
            self.add_updater(self.another_node_plucked_updater)
        else:
            self.add_updater(self.updater)

    #This generates the "pluck" function, it's just a fancy way of having a set of points where we can move a node that is being plucked
    #THis DOES NOT oscilate, we only want pull the node up and the function generates points in order for us to do that
    def pluck_function(self, t):
        #the entire period of the function must be the 4 times the pluck time, half the amplitude must be the length to pluck
        period = 4*self.time_to_strum
        return self.length_to_strum*np.sin(2*PI*(1/period)*t)

    #Adds the connecting lines or it smooths out the path depending on the option chosen
    def add_connecting_lines(self):
        if(self.smooth):
            self.add(VMobject(color = self.color))
            #if the rope is smooth we add a VMobject Path with nodes as points in it
            for i in range(1, self.number_nodes):
                self[self.number_nodes].append_vectorized_mobject(Line(start = self.x[i-1], end = self.x[i], stroke_width = self.thickness*20, color = self.color, stroke_opacity = self.opacity))
                self[self.number_nodes].make_smooth
        else:
            #otherwise we just make lines through the middle of the nodes
            for i in range(1,self.number_nodes):
                self.add(Line(start = self.x[i-1], end = self.x[i], stroke_opacity = self.opacity,stroke_width = self.thickness*30, color = self.color, opacity = self.opacity))
    
    #This is the function that updates either the lines between nodes or the smooth path after the nodes have moved
    def update_paths(self):
        if(self.smooth):
            temp_path = VMobject(color = self.color)
            #if the rope is smooth then we make a temp VMobject path with nodes as points in it
            for i in range(1, self.number_nodes):
                temp_path.append_vectorized_mobject(Line(start = self.x[i-1], end = self.x[i], stroke_opacity = self.opacity, stroke_width = self.thickness*20, color = self.color))
                temp_path.make_smooth
            self[self.number_nodes].become(temp_path)
        else:
            #If it's not smooth we just connect with lines
            for i in range(1, self.number_nodes):
                self[i+self.number_nodes-1].become(Line(self.x[i-1], self.x[i], stroke_width = self.thickness*30, stroke_opacity = self.opacity, color = self.color))
                
    #This is meant to play and animate the entire thing
    def put_into_motion(self):
        self.updater_adder()
    #The following are just helper functions for the updater function 

    #This holds a node at position index in place
    def hold_node_in_place(self, index):
        self.x[index] = self.start + self.length_between_centers*index*self.orientation
        self.v[index] = np.array([0,0,0])

    #This allows us to get a perpendicular vector that always points in the +y direction 
    def get_perpendicular_vector(self, vector):
        x = vector[0]
        y = vector[1]
        if(y>0):
            return np.array([y,-x,0])
        else:
            return np.array([-y, x, 0])

    #This displaces the node at position index an ammount function(time) where the function and times are given, and this allows for certian nodes to move and they can also move their
    #neighboring nodes as well using this
    def move_node_acoording_to_func(self, index, time, function):
        self.x[index] = self.start + self.length_between_centers*index*self.orientation + function(time)*self.get_perpendicular_vector(self.orientation)

    #This allows the velocity of nodes that are perhaps moving up or down to be set as they move
    def set_velocity_acoording_to_func(self, index, time, function):
        self.v[index] = function(time) * self.get_perpendicular_vector(self.orientation)
    

    #This sets the forces of a node in the list of spring and dampening forces, it depends on the main index the previous and the next one. If the node is at either end then 
    #This function still works, you just pass a -1 as the arguement that is out of bounds
    def set_forces(self, main_node_index, prev_node_index, next_node_index):
        # if(self.time>=self.cycles/self.frequency-5 and (main_node_index == 0 or main_node_index == 1 or main_node_index == 2) and self.time< self.cycles/self.frequency -5 + .1):
        #     print(main_node_index,": ", self.v[main_node_index])
       
        self.spring_force[main_node_index] = np.array([0,0,0])
        if(prev_node_index != -1):
            self.spring_force[main_node_index] += self.get_spring_force(self.x[main_node_index], self.x[prev_node_index])
        if(next_node_index != -1):
            self.spring_force[main_node_index] += self.get_spring_force(self.x[main_node_index], self.x[next_node_index])
        self.dampening_force[main_node_index] = np.array([0,0,0])
        self.dampening_force[main_node_index]+=self.get_dampening_force(self.v[main_node_index])
       
    #This functions runs the quick calculation of the fundemental frequency for a given setup with like BC or unlike BC
    def get_fundemental_freq(self, like_BC):
        if(like_BC):
            return np.sqrt(self.tension/self.linear_mass_density(self.length))/(2*self.length)
        else:
            return np.sqrt(self.tension/self.linear_mass_density(self.length))/(4*self.length)

    #This applies the net force and stores the calculated movement values in the self.x and self.v arrays 
    def apply_net_force_to_node(self, index, time_interval):
       
        extra_forces = self.net_force

        if(self.nodes_with_net_force.count(index)>0): #If the node has been designated a net force on it
            extra_forces= extra_forces + self.forces_on_lengths[self.nodes_with_net_force.index(index)] #admitedly inefficient but we add the force based on the index in nodes_with_net_force

        #self.apply_net_force_along_axis(index, self.get_perpendicular_vector(self.orientation), time_interval)
        self.v[index] += time_interval*(self.spring_force[index] + self.dampening_force[index] + extra_forces)/self.masses[index]
        self.x[index]+=self.v[index]*time_interval
    
    #This essentially allows us to apply net forces to a bunch of nodes at once
    def apply_net_force_to_nodes(self, start_index, end_index, time_interval):
        for i in range(start_index, end_index):
            self. apply_net_force_to_node(i, time_interval)

    #This allows us to apply a force along a certian axis. This is like if one of the ends is loose, we only allow it to oscilate in a direction perpendicular to the rope
    #or else it would shrivel in on itself
    def apply_net_force_along_axis(self, index, axis, time_interval): #The time interval is meant to be dt 
       
        extra_forces = self.net_force

        if(self.nodes_with_net_force.count(index)>0): #If the node has been designated a net force on it
            extra_forces = extra_forces + self.forces_on_lengths[self.nodes_with_net_force.index(index)] #admitedly inefficient but we add the force based on the index in nodes_with_net_force

        a_hat = axis/np.linalg.norm(axis) #making axis a unit vector
        delta_v = time_interval*(self.spring_force[index]+self.dampening_force[index]+extra_forces)/self.masses[index]
        v_proj = delta_v.dot(a_hat) #dotting to find the magnetude of the projection
        self.v[index] = self.v[index] + v_proj*a_hat
        self.x[index] += self.v[index]*time_interval


    #This function physically moves the nodes to where they need to be
    def update_nodes(self):
        for i in range(0, self.number_nodes):
                self[i].move_to(self.x[i])
    
    #This is the updater function, this is applied if the nodes are not strummed but the left node is driven
    def updater(self, rope, dt):

            #We check if the strum time is up first
            if(rope.time>= rope.cycles/rope.frequency):
                if(rope.left_end_fixed): #If the time is up we check if the node is meant to be fixed, if it is we hold it
                    rope.hold_node_in_place(0)
                else: #Otherwise we set the forces acoordingly
                    rope.set_forces(0, -1, 1)
            else:# if it isn't we keep driving the node acoording to the function
                rope.move_node_acoording_to_func(0, rope.time, rope.displacement_function)
                rope.set_velocity_acoording_to_func(0, rope.time, rope.velocity_function)

            #we now set the forces for the rest of the nodes 
            for i in range(1, rope.number_nodes-1):
                rope.set_forces(i, i-1, i+1)
            
            #We can then check if the right end is fixed where we have a simmilar situation
            if(rope.right_end_fixed):
                rope.hold_node_in_place(rope.number_nodes-1) #if it is we hold it

            else:
                rope.set_forces(rope.number_nodes-1,rope.number_nodes-2, -1) #Otherwise set forces

            #if we aren't still pulling one of the nodes up we apply a net force to the left end.
            if(not rope.left_end_fixed and rope.time>=rope.cycles/rope.frequency): #if we are still strumming we keep the end in place so the string doesnt just move up
                rope.apply_net_force_along_axis(0, rope.get_perpendicular_vector(rope.orientation), dt)

            #We move the rest of the nodes
            rope.apply_net_force_to_nodes(1, rope.number_nodes-1, dt)

            #simmilar to what we did above we apply a force to the right end 
            if(not rope.right_end_fixed):
                rope.apply_net_force_along_axis(rope.number_nodes-1, rope.get_perpendicular_vector(rope.orientation), dt)

            if(not rope.right_end_fixed and not rope.left_end_fixed):
                vector = rope.out_of_bounds()
                for i in range(0, rope.number_nodes):
                    rope.x[i] += vector

            #Update the actual physical look of the nodes and paths acoording to the new data just calculated 
            rope.update_nodes()
            rope.update_paths()
            rope.time+=dt
        
    #This is the updater that moves the string when a certian node is plucked
    def another_node_plucked_updater(self, rope, dt):           
            #we move the node to be plucked first, and we have it's y position be dictated by a sin wave, only if it's the strum time
            if(rope.time<rope.time_to_strum):
                rope.move_node_acoording_to_func(rope.node_to_strum, rope.time, rope.pluck_function)
            #we then check whether or not the the nodes being held hold should be held at this time
            if(rope.time<rope.time_to_hold or rope.hold_indefinetly):
                for node in rope.nodes_to_hold:
                    rope.hold_node_in_place(node)
            #If we are NOT strumming we must act appropriatley at the boundaries set the forces or hold it in place depending on what was specified in config
            if(rope.time >= rope.time_to_strum):
                if(rope.left_end_fixed):
                    rope.hold_node_in_place(0)                   
                #If the end isn't fixed we let it move freely
                else:
                    rope.set_forces(0, -1, 1)
            #If we are still strumming we just simply hold it in place
            else:
                rope.hold_node_in_place(0)

            #Setting the forces for all the other nodes    
            for i in range(1, rope.number_nodes-1):

                if(rope.time<rope.time_to_strum and i == rope.node_to_strum): #If the node is the one being strummed we don't set forces for it
                    continue
                if((rope.time<rope.time_to_hold or rope.hold_indefinetly) and rope.nodes_to_hold.count(i)>0): #If the nodes are being held then we skip it it's movement has already been designated
                    continue
                rope.set_forces(i, i-1, i+1) #Set the forces of the ropes otherwise
            
            if(rope.right_end_fixed): #Depending on whether or not an end is able to move in config we either hold or set the nodes forces
                rope.hold_node_in_place(rope.number_nodes-1)
                
            else:
                rope.set_forces(rope.number_nodes-1, rope.number_nodes-2, -1)

            #Movinf the first node if not fixed
            if(not rope.left_end_fixed):
                rope.apply_net_force_along_axis(0, rope.get_perpendicular_vector(rope.orientation), dt)

            #moving the other nodes
            rope.apply_net_force_to_nodes(1, rope.number_nodes-1, dt)

            #moving the last node if not fixed
            if(not rope.right_end_fixed):
                rope.apply_net_force_along_axis(rope.number_nodes-1, rope.get_perpendicular_vector(rope.orientation), dt)            
           
           #physically moving each circle to the correct place
            rope.update_nodes()
            rope.update_paths()
            rope.time+=dt
    #TO BE IMPROVED
    #Making a new move_to function so that the rope wont go haywire when its moved
    def out_of_bounds(self):
        difference = self.start - self.x[0]
        if(np.linalg.norm(difference)>self.amplitude):
            return difference - 2*self.amplitude*self.get_perpendicular_vector(self.orientation)
        else:
            return np.array([0,0,0])

        

    def update_after_moved(self):
        self.start = self[0].get_center()
        for i in range(0,self.number_nodes):
            self.move_node_acoording_to_func(i,0,lambda x: 0)

#The theoretical rope is essentailly just a rope with a different updater
class TheoreticalRope(Rope):
    CONFIG = {
        "set_manually": False
    }
    #This function takes the x position as an argument and returns another function which only involves time that tells the nodes where to go
    def generate_moving_function(self, x_position):
        # if(not self.right_end_fixed or not self.left_end_fixed):
        #     phase_shift = 0
        #     x_position = self.wavelength - x_position
        # else:
        phase_shift = 0
        k = 2*PI/self.wavelength
        omega = 2*PI*self.frequency
        def moving_function(time):

            return 2*self.amplitude*np.sin(k*x_position - phase_shift)*np.cos(omega*time)
        return moving_function
        
    def updater(self, rope, dt):
        #moving every single node acoording to the theoretical function
        for i in range(0, rope.number_nodes):
            #this is just creating a variable which notes the position of the ith node with respect to the begining of the node
            x_pos = rope.length_between_centers*i
            rope.move_node_acoording_to_func(i, rope.time, rope.generate_moving_function(x_pos))
        #The next thing we do is update the visuals and we're done!
        rope.update_nodes()
        rope.update_paths()
        rope.time += dt

class Test(Scene):
    def construct(self):
        rope = TheoreticalRope(harmonic = 1, left_end_fixed = True, right_end_fixed = True, length = 4)
        self.add(rope)
        self.wait()
        rope.put_into_motion()
        self.wait(3)
    



#Notes:
#Like Boundary conditions on the actual rope object are 1/4 of a period off
#Unlike BC are done differently you are required to wait the exact amount of time. Do half the cycles tho


class RopesandStringsScene(Scene):
    
    CONFIG = {
        "number_ropes": 10,
        "mixed_harmonics": [1,3,5,7,9], #The odd harmonics 
        "like_harmonics": [1,2,3,5,6], #The even harmonics
        "both_closed": [True, True, True, True, True], #Are the like BC both closed or open
        "right_loose": [True, True, True, True, True], #Are the mixed BC loose on the right end or the left one
        "sim_colors": [RED, BLUE, GREEN, PURPLE, YELLOW, GOLD, PINK, WHITE, MAROON, TEAL], #List of colors for the rope simulation
        "theo_colors": [BLUE_C, RED_C, PURPLE_C, ORANGE, GREEN_SCREEN, BLUE, TEAL_C, YELLOW, RED_C, WHITE],
        "theo_opacity":0.0, #TO DO
        "grid_buff": (MED_SMALL_BUFF+ SMALL_BUFF)/2-0.05,
        "rope_config": {
            "tension": 200,
            "spring_k": 2500,
            "number_nodes":50,
            "linear_mass_density": lambda x: 10,
            "amplitude": 0.25,
            "set_manually": False,
            "harmonic": 5,
            "left_end_fixed": False,
            "right_end_fixed": False,
            "dampening_constant": 0,
            "start": ORIGIN,
            "orientation": RIGHT,
            "cycles": 5,
            "length":4,
            "color": WHITE,
            "smooth": False,
            "opacity": 1.0
        },

        "background_rect_setup":{
            "stroke_width": 5, 
            "fill_opacity": 0.0, 
            "buff": (MED_LARGE_BUFF+LARGE_BUFF)/2-.05, 
            "color": WHITE
        }
    }
    def construct(self):
        self.timer = ValueTracker(0)
        self.ropes = VGroup() #We make a ropes VGroup for easy arrangement of the objects
        self.ropes_list = [] #We make a rope list where each rope can be set into motion from
        self.make_all_ropes()
        self.play(ShowCreation(self.ropes))

        for i in range(0, len(self.ropes_list)):
            self.ropes_list[i].update_after_moved()
        self.drive_ropes()
        self.wait(45)
        
        
    #We create a V group containing ropes and a frame, passing the index we are referring to and from what list
    def make_rope(self, index, mixed):
        rope_and_frame_and_text = VGroup()
        conf = dict(self.rope_config)
        #Depending on what the user feeds in, mixed or otherwise we need to choose the correct lists from config to set up the rope
        if(mixed):
            conf["harmonic"] = self.mixed_harmonics[index]
            conf["right_end_fixed"] = not self.right_loose[index]
            conf["left_end_fixed"] = self.right_loose[index]
            conf["cycles"] = self.mixed_harmonics[index]/2
            index_2 = index

        else:
            conf["harmonic"] = self.like_harmonics[index]
            conf["right_end_fixed"] = self.both_closed[index]
            conf["left_end_fixed"] = self.both_closed[index]
            conf["cycles"] = self.like_harmonics[index]
            index_2 = 5+index #This is the index used for the colors and stuff
        
        #Now we make the actual rope and the theoretical rope
        
        conf["color"]= self.sim_colors[index_2]
        rope = Rope(**conf)
        
        conf["color"] = self.theo_colors[index_2]
        conf["opacity"] = self.theo_opacity
        theo_rope = TheoreticalRope(**conf)

        rope_and_frame_and_text.add(rope, theo_rope)
        
        
        rope_rectangle = BackgroundRectangle(rope, **self.background_rect_setup)
        rope_and_frame_and_text.add_to_back(rope_rectangle)
        
        freq = int(rope.frequency*1000)
        new_freq = freq/1000
        #Making the labels
        harm = TexMobject(r"n = ", str(rope.harmonic), color = self.sim_colors[index_2])
        freq = TexMobject(r"f_{0} =", str(new_freq), "Hz", color = self.sim_colors[index_2])
        text = VGroup(harm, freq)
        text.scale(0.4)
        harm.next_to(freq, RIGHT, buff = SMALL_BUFF)
        text.next_to(rope_rectangle.get_center() + UP*(rope_rectangle.height/2), DOWN, buff = SMALL_BUFF)

        rope_and_frame_and_text.add(text)
        
        

        #Adding to the self V Group
        self.ropes_list.append(rope)
        self.ropes_list.append(theo_rope)
        self.ropes.add(rope_and_frame_and_text)


    
    def make_all_ropes(self):
        for i in range(0, self.number_ropes//2):
            self.make_rope(i, False) #Makes one even rope and one odd rope
            self.make_rope(i, True)
        self.ropes.arrange_submobjects_in_grid(n_rows = 5, n_cols = 2, buff = self.grid_buff)

    def drive_ropes(self):        
        for i in range(1,2*self.number_ropes,2):
            self.ropes_list[i-1].put_into_motion()
        for i in range(1,2*self.number_ropes, 2):
            self.ropes_list[i].add_updater(self.driving_ropes_updater)
    
    #TO DO/TO BE IMPROVED THEORETICAL ROPE TIMING FOR DEMONSTRATION PURPOSES    
    def driving_ropes_updater(self, rope, dt):
        if(rope.right_end_fixed == rope.left_end_fixed):
            if (self.timer.get_value() >= (rope.cycles)/rope.frequency):
                rope.put_into_motion()
        else:
            if(self.timer.get_value() >= (rope.cycles)/(rope.frequency)):
                rope.put_into_motion()
    



    
    