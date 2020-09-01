#!/usr/bin/env python

from big_ol_pile_of_manim_imports import *

class AngleElbow(VGroup):
    CONFIG = {
        "color": WHITE,
        "guide_dir": PI/4,
        "arc_color": WHITE
        
        }
    def __init__(self, start_point, length, angle, **kwargs):
        digest_config(self,kwargs)
        VGroup.__init__(self)
        guide_line = Line(start_point, start_point+length*np.array([np.cos(self.guide_dir), np.sin(self.guide_dir), 0]), stroke_width = 0)
        line_1 = Line(start_point, start_point + length*np.array([np.cos(self.guide_dir - angle/2), np.sin(self.guide_dir - angle/2),0]), color = self.color)
        line_2 = Line(start_point, start_point + length*np.array([np.cos(self.guide_dir + angle/2), np.sin(self.guide_dir + angle/2),0]), color  = self.color)
        self.add(guide_line)
        self.add(line_1)
        self.add(line_2)
        self.angle = angle
        self.add()
    def make_angle(self, angle):
        self[1].set_angle(self.guide_dir - angle/2)
        self[2].set_angle(self.guide_dir + angle/2)

class SecondScene(Scene):
    CONFIG={
        "RT_THREE": 1.732,
        "theta_in": PI/2,
        "phi_in": 7*PI/6,
        "xi_in": 11*PI/6,
        "xi_fin": 4*PI/3,
        "phi_fin": PI,
        "xi_fin_2": 9*PI/4,
        "phi_fin_2": 3*PI/2,
        "phi_extreme_1": 4*PI/3,
        "xi_extreme_1": 4*PI/3+0.2,
        "phi_extreme_2": 2*PI/3,
        "xi_extreme_2": 5*PI/3,
        "circle_radius": 2,
        "arc_radius": 0.3,
        "main_line_size": 4,
        "spoke_line_size": 2,
        "m_scale": 1.5,
        "adding_line_size": 4,
        "angle_elbow_length": 0.75,
        "colors_elbow": [RED, BLUE, YELLOW]
        
        }

    def construct(self):
        RT_THREE = 1.732
        RADIUS = 2
        theta = ValueTracker(self.theta_in)
        phi = ValueTracker(self.phi_in)
        xi = ValueTracker(self.xi_in)
        value_trackers = [theta, phi, xi]
        #Start with an equilateral of sidelength
        side_length = 5
        center = VectorizedPoint(np.array([0,-0.7,0]))
        #Making dynamic points that move with the triangle
        V_A = VectorizedPoint(np.array([self.circle_radius*np.cos(theta.get_value()), self.circle_radius*np.sin(theta.get_value()),0]+self.m_scale*center.get_center()))
        V_B = VectorizedPoint(np.array([self.circle_radius*np.cos(phi.get_value()), self.circle_radius*np.sin(phi.get_value()),0])+self.m_scale*center.get_center())
        V_C = VectorizedPoint(np.array([self.circle_radius*np.cos(xi.get_value()), self.circle_radius*np.sin(xi.get_value()),0])+self.m_scale*center.get_center())
        
        V_A.add_updater(lambda x: x.become(VectorizedPoint(np.array([self.circle_radius*np.cos(theta.get_value()), self.circle_radius*np.sin(theta.get_value()),0])+self.m_scale*center.get_center())))
        V_B.add_updater(lambda x: x.become(VectorizedPoint(np.array([self.circle_radius*np.cos(phi.get_value()), self.circle_radius*np.sin(phi.get_value()),0])+self.m_scale*center.get_center())))
        V_C.add_updater(lambda x: x.become(VectorizedPoint(np.array([self.circle_radius*np.cos(xi.get_value()), self.circle_radius*np.sin(xi.get_value()),0])+self.m_scale*center.get_center())))

        d_points = [V_A, V_B, V_C]
        d_group = VGroup(V_A, V_B, V_C)
        #Points where the arcs are going to go

        angle_A_1 = VectorizedPoint(V_A.get_center()+ self.arc_radius*(V_B.get_center()-V_A.get_center())/np.linalg.norm(V_B.get_center()-V_A.get_center()))
        angle_A_2 = VectorizedPoint(V_A.get_center() - self.arc_radius*(V_A.get_center() - V_C.get_center())/np.linalg.norm(V_C.get_center()-V_A.get_center()))
        angle_A_1.add_updater(lambda x: x.become(VectorizedPoint(V_A.get_center()+ self.arc_radius*((V_B.get_center()-V_A.get_center())/np.linalg.norm(V_B.get_center()-V_A.get_center())))))
        angle_A_2.add_updater(lambda x: x.become(VectorizedPoint(V_A.get_center() - self.arc_radius*((V_A.get_center() - V_C.get_center())/np.linalg.norm(V_C.get_center()-V_A.get_center())))))
        
        angle_B_1 = VectorizedPoint(V_B.get_center()+ self.arc_radius*(V_C.get_center()-V_B.get_center())/np.linalg.norm(V_C.get_center()-V_B.get_center()))
        angle_B_2 = VectorizedPoint(V_B.get_center() + self.arc_radius*(V_A.get_center() - V_B.get_center())/(np.linalg.norm(V_A.get_center()-V_B.get_center())))
        angle_B_1.add_updater(lambda x: x.become(VectorizedPoint(V_B.get_center()+ self.arc_radius*((V_C.get_center()-V_B.get_center())/np.linalg.norm(V_C.get_center()-V_B.get_center())))))
        angle_B_2.add_updater(lambda x: x.become(VectorizedPoint(V_B.get_center() + self.arc_radius*((V_A.get_center() - V_B.get_center())/np.linalg.norm(V_A.get_center()-V_B.get_center())))))

        angle_C_1 = VectorizedPoint(V_C.get_center()+ self.arc_radius*(V_B.get_center()-V_C.get_center())/np.linalg.norm(V_B.get_center()-V_C.get_center()))
        angle_C_2 = VectorizedPoint(V_C.get_center() + self.arc_radius*(V_A.get_center() - V_C.get_center())/np.linalg.norm(V_A.get_center()-V_C.get_center()))
        angle_C_1.add_updater(lambda x: x.become(VectorizedPoint(V_C.get_center()+ self.arc_radius*((V_B.get_center()-V_C.get_center())/np.linalg.norm(V_B.get_center()-V_C.get_center())))))
        angle_C_2.add_updater(lambda x: x.become(VectorizedPoint(V_C.get_center() + self.arc_radius*((V_A.get_center() - V_C.get_center())/np.linalg.norm(V_A.get_center()-V_C.get_center())))))

        def getUnitVector(vector):
            return vector/np.linalg.norm(vector)
        #making the decimal number and tex
        a_value = DecimalNumber(np.arccos(getUnitVector(V_B.get_center()-V_A.get_center()).dot(getUnitVector(V_C.get_center()-V_A.get_center())))/DEGREES).add_updater(lambda x: x.set_value(np.arccos(getUnitVector(V_B.get_center()-V_A.get_center()).dot(getUnitVector(V_C.get_center()-V_A.get_center())))/DEGREES))
        a_label = TexMobject("a =", tex_to_color_map = {"a":RED})
        a_label.next_to(a_value, LEFT, 0.3)
        a_label.add_updater(lambda x: x.next_to(a_value, LEFT, 0.3))

        b_value = DecimalNumber(np.arccos(getUnitVector(V_A.get_center()-V_B.get_center()).dot(getUnitVector(V_C.get_center()-V_B.get_center())))/DEGREES).add_updater(lambda x: x.set_value(np.arccos(getUnitVector(V_A.get_center()-V_B.get_center()).dot(getUnitVector(V_C.get_center()-V_B.get_center())))/DEGREES))
        b_label = TexMobject("b =", tex_to_color_map = {"b":BLUE})
        b_label.next_to(b_value, LEFT, 0.3)
        b_label.add_updater(lambda x: x.next_to(b_value, LEFT, 0.3))

        c_value = DecimalNumber(np.arccos(getUnitVector(V_B.get_center()-V_C.get_center()).dot(getUnitVector(V_A.get_center()-V_C.get_center())))/DEGREES).add_updater(lambda x: x.set_value(np.arccos(getUnitVector(V_B.get_center()-V_C.get_center()).dot(getUnitVector(V_A.get_center()-V_C.get_center())))/DEGREES))
        c_label = TexMobject("c =", tex_to_color_map = {"c":YELLOW})
        c_label.next_to(c_value, LEFT, 0.3)
        c_label.add_updater(lambda x: x.next_to(c_value, LEFT, 0.3))
        values_arr = [a_value, b_value, c_value]
        labels = VGroup(a_label, b_label, c_label)
        labels.arrange_submobjects(DOWN)
        total_text = TextMobject("Total:")
       
        degree_labels = []
        for i in range(0,3):
            degree_labels.append(TexMobject(r"\circ"))

        degree_labels[0].add_updater(lambda x: x.next_to(a_value, RIGHT+0.1*UP, 0.1))
        degree_labels[1].add_updater(lambda x: x.next_to(b_value, RIGHT+0.1*UP, 0.1))
        degree_labels[2].add_updater(lambda x: x.next_to(c_value, RIGHT+0.1*UP, 0.1))

        degree_labels.append(TexMobject(r"\circ"))
        add_line = Line(ORIGIN,self.adding_line_size*RIGHT, color = WHITE).add_updater(lambda x: x.move_to(c_label.get_center()+0.4*DOWN + 0.9*RIGHT ))
        add_symbol = TexMobject("+").add_updater(lambda x: x.next_to(c_value, RIGHT, 0.5))
        A_sum = DecimalNumber(a_value.get_value()+b_value.get_value()+c_value.get_value()).add_updater(lambda x: x.set_value(a_value.get_value()+b_value.get_value()+c_value.get_value()))
        A_sum.add_updater(lambda x: x.next_to(c_label, 1.9*DOWN+0.4*RIGHT, 0.3))
        degree_labels[3].add_updater(lambda x: x.next_to(A_sum, 1.1*RIGHT+0.2*UP, 0.1))
        total_text.add_updater(lambda x: x.next_to(A_sum, LEFT, 0.3))
        values = VGroup( a_value, b_value, c_value, add_line, add_symbol, A_sum, degree_labels[0], degree_labels[1], degree_labels[2], degree_labels[3], total_text)
        values.arrange_submobjects(DOWN)
        values.to_corner(UL, 1)
        values.shift(0.5*UP)
       

        #creating triangle 
        triangle = Polygon(V_A.get_center(), V_B.get_center(), V_C.get_center(), color = WHITE)
        triangle.add_updater(lambda x: x.become(Polygon(V_A.get_center(), V_B.get_center(), V_C.get_center(), color = WHITE)))

        #creating angle arc
        angle_A = ArcBetweenPoints(angle_A_1.get_center(), angle_A_2.get_center(), color = RED)
        angle_A.add_updater(lambda x: x.become(ArcBetweenPoints(angle_A_1.get_center(), angle_A_2.get_center(), color =  RED)))  
        
        
        angle_B = ArcBetweenPoints(angle_B_1.get_center(), angle_B_2.get_center(), color = BLUE)
        angle_B.add_updater(lambda x: x.become(ArcBetweenPoints(angle_B_1.get_center(), angle_B_2.get_center(), color =  BLUE)))
      

        angle_C = ArcBetweenPoints(angle_C_1.get_center(), angle_C_2.get_center(), -TAU/4, color = YELLOW)
        angle_C.add_updater(lambda x: x.become(ArcBetweenPoints(angle_C_1.get_center(), angle_C_2.get_center(), -TAU/4, color = YELLOW)))
        

        #creating labels for the triangles sides
        V_label_A = TexMobject("a", tex_to_color_map = {"a":RED}).add_updater(lambda x: x.next_to(V_A, getUnitVector(V_A.get_center()))) 
        V_label_B = TexMobject("b", tex_to_color_map = {"b":BLUE}).add_updater(lambda x: x.next_to(V_B, getUnitVector(V_B.get_center())))
        V_label_C = TexMobject("c", tex_to_color_map = {"c":YELLOW}).add_updater(lambda x: x.next_to(V_C, getUnitVector(V_C.get_center())))

        V_label_A.add_updater(lambda x: x.next_to(V_A, getUnitVector(V_A.get_center() - self.m_scale*center.get_center()))) 
        V_label_B.add_updater(lambda x: x.next_to(V_B, getUnitVector(V_B.get_center() - self.m_scale*center.get_center())))
        V_label_C.add_updater(lambda x: x.next_to(V_C, getUnitVector(V_C.get_center() - self.m_scale*center.get_center())))

        t_group = VGroup(V_A, V_B, V_C, triangle, angle_A, angle_B, angle_C, V_label_A, V_label_B, V_label_C, V_A, V_B, V_C, angle_A_1, angle_A_2, angle_B_1, angle_B_2, angle_C_1, angle_C_2 )
        arc_group = VGroup(angle_A, angle_B, angle_C, angle_A_1, angle_A_2, angle_B_1, angle_B_2, angle_C_1, angle_C_2)
        label_group = VGroup( V_label_A, V_label_B, V_label_C)


        #Making the lines that turn to angles
        bottom_line = Line(self.main_line_size/2*LEFT, self.main_line_size/2*RIGHT, color = BLACK, stroke_width = 0)
        bottom_line_phony_1 = Line(ORIGIN, self.main_line_size/2*RIGHT, color = PURPLE)
        bottom_line_phony_2 = Line(ORIGIN, self.main_line_size/2*LEFT, color = GREEN)
        spoke_1 = Line(ORIGIN, self.spoke_line_size * getUnitVector(V_B.get_center()-V_A.get_center()), color = PURPLE)
        spoke_2 = Line(ORIGIN, self.spoke_line_size*getUnitVector(V_C.get_center()-V_A.get_center()), color = GREEN)
        spoke_1.add_updater(lambda x: x.set_angle(np.arccos(getUnitVector(V_A.get_center()-V_B.get_center()).dot(getUnitVector(V_C.get_center()-V_B.get_center())))))
        spoke_2.add_updater(lambda x: x.set_angle(PI-np.arccos(getUnitVector(V_A.get_center()-V_C.get_center()).dot(getUnitVector(V_B.get_center()-V_C.get_center())))))
        dot_mid  = Dot(spoke_1.get_start())
        #Making arcs for the lines
        line_arc_B = Arc(radius = self.arc_radius, arc_center = spoke_1.get_start(), start_angle = 0, angle = spoke_1.get_angle(), color = BLUE)
        line_arc_C = Arc(radius = self.arc_radius, arc_center = spoke_2.get_start(), start_angle = spoke_2.get_angle(), angle = PI-spoke_2.get_angle(), color = YELLOW)
        line_arc_A = Arc(radius = self.arc_radius, arc_center = spoke_1.get_start(), start_angle = spoke_1.get_angle(), angle = spoke_2.get_angle()-spoke_1.get_angle(), color = RED)
        
        line_arc_B.add_updater(lambda x: x.become(Arc(radius = self.arc_radius, arc_center = spoke_1.get_start(), start_angle = 0, angle = spoke_1.get_angle(), color = BLUE)))
        line_arc_A.add_updater(lambda x: x.become(Arc(radius = self.arc_radius, arc_center = spoke_1.get_start(), start_angle = spoke_1.get_angle(), angle = spoke_2.get_angle()-spoke_1.get_angle(), color = RED)))
        line_arc_C.add_updater(lambda x: x.become(Arc(radius = self.arc_radius, arc_center = spoke_2.get_start(), start_angle = spoke_2.get_angle(), angle = PI-spoke_2.get_angle(), color = YELLOW)))
     
        
        #Making labels for the arcs
        l_A = TexMobject("a", color = RED).add_updater(lambda x : x.next_to(line_arc_A, spoke_1.get_unit_vector()+spoke_2.get_unit_vector()/2, 1.6))
        l_B = TexMobject("b", color = BLUE).add_updater(lambda x : x.next_to(line_arc_B, (spoke_1.get_unit_vector()+RIGHT)/2, 2))
        l_C = TexMobject("c", color = YELLOW).add_updater(lambda x : x.next_to(line_arc_C, (spoke_2.get_unit_vector()+LEFT)/2, 2))

        lines = VGroup(bottom_line_phony_1, bottom_line_phony_2, bottom_line, spoke_1, spoke_2, line_arc_B, line_arc_A, line_arc_C, l_A, l_B, l_C, dot_mid)
        lines.shift(2*DOWN+4.5*LEFT)
        line_angles = VGroup(line_arc_A, line_arc_B, line_arc_C)
        line_labels = VGroup(l_A, l_B, l_C)
        just_lines = VGroup(bottom_line_phony_1, bottom_line_phony_2, bottom_line, spoke_1, spoke_2, dot_mid)

        #supplimentary elbows:
        elbs = VGroup()
        elbs_labels = VGroup(TexMobject("a", color = RED), TexMobject("b", color = BLUE), TexMobject("c", color = YELLOW))
        for i in range(0,3):
            elbs.add(AngleElbow(ORIGIN, self.angle_elbow_length, values[i].get_value(), color = self.colors_elbow[i], guide_dir = PI/8))
     
        elbs[0].add_updater(lambda x: x.make_angle(a_value.get_value()*DEGREES))
        

        elbs[1].add_updater(lambda x: x.make_angle(b_value.get_value()*DEGREES))
        

        elbs[2].add_updater(lambda x: x.make_angle(c_value.get_value()*DEGREES))
       

        elbs.arrange_submobjects(LEFT, buff = 1.5)
        elbs_labels.arrange_submobjects(LEFT, buff = 2)
        elbs_labels.to_edge(UP, buff = 0.3)
        elbs.to_edge(UP)
        elbs.shift(2*RIGHT)
        elbs_labels.shift(2*RIGHT)
        elbs.shift(0.75*DOWN)

        #temporary objects
        temp_lines = []
        temp_dots = []
        self.play(ShowCreation(triangle), ShowCreation(d_group), ShowCreation(center))
        verts = triangle.get_vertices()
        for i in range(0,3):
            temp_dots.append(Dot(verts[i]))
            for j in range(0,3):
                if not((verts[i]==verts[j]).all()):
                   temp_lines.append(Line(start = verts[i], end = 2*getUnitVector(verts[j]-verts[i])+verts[i]))
        def getAngle(vector):
            if(vector[1]<0):
                return 2*PI - np.arccos(getUnitVector(vector).dot(np.array([1,0,0])))
            else:
                return np.arccos(getUnitVector(vector).dot(np.array([1,0,0])))
        
            #adjusting colors
        for i in range(0,2):
            temp_lines[i].set_color(ORANGE)
        for i in range(2, 4):
            temp_lines[i].set_color(GREEN)
        for i in range(4,6):
            temp_lines[i].set_color(PURPLE)
        #making respective VGroups
        counter = 0
        temp_lines[0].add_updater(lambda x: x.set_angle(getAngle(V_B.get_center() - V_A.get_center())))
        temp_lines[1].add_updater(lambda x: x.set_angle(getAngle(V_C.get_center() - V_A.get_center())))

        temp_lines[2].add_updater(lambda x: x.set_angle(getAngle(V_A.get_center() - V_B.get_center())))
        temp_lines[3].add_updater(lambda x: x.set_angle(getAngle(V_C.get_center() - V_B.get_center())))

        temp_lines[4].add_updater(lambda x: x.set_angle(getAngle(V_A.get_center() - V_C.get_center())))
        temp_lines[5].add_updater(lambda x: x.set_angle(getAngle(V_B.get_center() - V_C.get_center())))

        #temp_lines[0].add_updater(lambda x: x.set_start_and_end(temp_dots[0].get_center(), x.get_end()))
        #temp_lines[1].add_updater(lambda x: x.set_start_and_end(temp_dots[0].get_center(), x.get_end()))

        #temp_lines[2].add_updater(lambda x: x.set_start_and_end(temp_dots[1].get_center(), x.get_end()))
        #temp_lines[3].add_updater(lambda x: x.set_start_and_end(temp_dots[1].get_center(), x.get_end()))

        #temp_lines[4].add_updater(lambda x: x.set_start_and_end(temp_dots[2].get_center(), x.get_end()))
        #temp_lines[5].add_updater(lambda x: x.set_start_and_end(temp_dots[2].get_center(), x.get_end()))
        temp_elbows = []
        counter = 0
        for i in range(0,3):
            temp_elbows.append(VGroup(temp_lines[counter], temp_lines[counter+1], temp_dots[i]))
            counter+=2
        all_elbows = VGroup(temp_elbows[0], temp_elbows[1], temp_elbows[2])
        
        ##final group of lines

        ##Animating 
        self.wait()
        self.play(*[ShowCreation(grp) for grp in temp_elbows])
        self.wait()
        self.play(Write(label_group))
        self.wait()
        self.play(ShowCreation(arc_group))
        self.wait()
        self.play(Write(values[0]), Write(values[1]), Write(values[2]))
        self.play(Write(a_label), Write(b_label), Write(c_label))
        self.play(Write(values[6]), Write(values[7]), Write(values[8]))
        
        self.wait()
        self.play(temp_elbows[0].shift,1.5*getUnitVector(verts[0]-triangle.get_center()), temp_elbows[1].shift,1.5*getUnitVector(verts[1]-triangle.get_center()), temp_elbows[2].shift,1.5*getUnitVector(verts[2]-triangle.get_center()))
        
        self.wait()

        temp_elbows[0].add_updater(lambda x: x.move_to(d_points[0].get_center() + np.linalg.norm(x.get_center() - d_points[0].get_center())* getUnitVector(d_points[0].get_center()-triangle.get_center())))
        temp_elbows[1].add_updater(lambda x: x.move_to(d_points[1].get_center() + np.linalg.norm(x.get_center() - d_points[1].get_center())*getUnitVector(d_points[1].get_center()-triangle.get_center())))
        temp_elbows[2].add_updater(lambda x: x.move_to(d_points[2].get_center() + np.linalg.norm(x.get_center() - d_points[2].get_center())*getUnitVector(d_points[2].get_center()-triangle.get_center())))
        
        self.play(phi.set_value, 4*PI/3-0.2, xi.set_value,2*PI-0.2, rate_func = smooth, run_time = .5)
        self.play(phi.set_value, 7*PI/6, xi.set_value, 11*PI/6, rate_func = smooth, run_time = .5)

        self.wait()

        temp_elbows[0].clear_updaters()
        temp_elbows[1].clear_updaters()
        temp_elbows[2].clear_updaters()

        self.play(temp_elbows[2].move_to, dot_mid.get_center()+temp_elbows[2].get_center()-temp_dots[2].get_center())
        self.play(Rotate(temp_elbows[0],PI,about_point = temp_dots[0].get_center()))
        self.play(temp_elbows[0].move_to, dot_mid.get_center()+temp_elbows[0].get_center()-temp_dots[0].get_center())
        self.play(temp_elbows[1].move_to, dot_mid.get_center()+temp_elbows[1].get_center()-temp_dots[1].get_center())
        
        self.wait()
        self.play(ShowCreation(line_angles), Write(line_labels))
        self.play(Write(values[3]), Write(values[5]))
        self.play(Write(values[4]), Write(values[9]), Write(values[10]))
        self.add(just_lines)
        self.remove(*[elbow for elbow in temp_elbows])
        self.wait()
        self.play(ShowCreation(elbs))
        self.play(Write(elbs_labels))
        self.play(center.move_to,np.array([3,-0.7,0]))

        self.wait(1)
        self.play(phi.set_value,self.phi_fin, xi.set_value,self.xi_fin, rate_func = smooth, run_time = 6)
        self.wait(.75)
        self.play(phi.set_value,self.phi_fin_2, xi.set_value,self.xi_fin_2, rate_func = smooth, run_time = 7)
        self.wait(.75)
        self.play(phi.set_value, self.phi_extreme_1, xi.set_value, self.xi_extreme_1, rate_func = smooth, run_time = 6)
        self.wait(0.75)
        self.play(phi.set_value, self.phi_extreme_2, xi.set_value, self.xi_extreme_2, rate_func = smooth, run_time = 4)
        self.wait()
        
        
# See old_projects folder for many, many more
