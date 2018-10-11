#!/usr/bin/env python

# ---------------------------------------------------------------------------
# Licensing Information: You are free to use or extend these projects for
# education or reserach purposes provided that (1) you retain this notice
# and (2) you provide clear attribution to UC Berkeley, including a link
# to http://barc-project.com
#
# Attibution Information: The barc project ROS code-base was developed at UC
# Berkeley in the Model Predictive Control (MPC) lab by Jon Gonzales
# (jon.gonzales@berkeley.edu) and Greg Marcil (grmarcil@berkeley.edu). The cloud
# services integation with ROS was developed by Kiet Lam
# (kiet.lam@berkeley.edu). The web-server app Dator was based on an open source
# project by Bruce Wootton
# ---------------------------------------------------------------------------

# README: This node serves as an outgoing messaging bus from odroid to arduino
# Subscribes: steering and motor commands on 'ecu'
# Publishes: combined ecu commands as 'ecu_pwm'

from rospy import init_node, Subscriber, Publisher, get_param, get_rostime
from rospy import Rate, is_shutdown, ROSInterruptException, spin, on_shutdown
from barc.msg import ECU
import rospy
import numpy as np

def srvOutput2Angle(fbk_srv):
    # angle_rad =  -0.003530958631043808 *fbk_srv +  1.0861319262672648
    angle_rad =  -0.003325686873493677 *fbk_srv +  1.1045130391911997
    return angle_rad


class low_level_control(object):
    motor_pwm = 90
    servo_pwm = 90
    str_ang_max = 30
    str_ang_min = -40
    ecu_pub = 0
    ecu_cmd = ECU()
    sel_car = rospy.get_param("/low_level_controller/car")
    pid_active = False

    recorded_servo = [0.0]*int(20)
    fbk_servo = 0.0
    commanded_steering = 0.0
    
    def fbk_servo_callback(self,data ):
        """Unpack message from sensor, ENC"""


        if self.pid_active == True:
            self.recorded_servo.pop(0)
            self.recorded_servo.append(data.servo)
            self.value_servo = np.sum(self.recorded_servo)/len(self.recorded_servo)

            steering_out = srvOutput2Angle(self.value_servo) #-0.003530958631043808*fbk_srv.value + 1.0861319262672648
            PIDController.solve(float(self.commanded_steering), float(steering_out))
            self.commanded_steering = PIDController.Steering

    def pwm_converter_callback(self, msg):

        # translate from SI units in vehicle model
        # to pwm angle units (i.e. to send command signal to actuators)
        # convert desired steering angle to degrees, saturate based on input limits

        # Old servo control:
        # self.servo_pwm = 91.365 + 105.6*float(msg.servo)
        # New servo Control
        # if msg.servo < 0.0:         # right curve
        #     self.servo_pwm = 95.5 + 118.8*float(msg.servo)
        # elif msg.servo > 0.0:       # left curve
        #     self.servo_pwm = 90.8 + 78.9*float(msg.servo)
        if self.pid_active == False:
            self.commanded_steering = msg.servo

        if self.sel_car == "OldBARC":
            # if msg.servo <=  -0.28427866720276546 :
            #     self.servo_pwm = (float(msg.servo) +  0.7667652891218538 ) /  0.008464677577527866
            # elif msg.servo >=  -0.2842786672027673  and msg.servo <=  -0.26318686746463726 :
            #     self.servo_pwm = (float(msg.servo) +  0.8853949597394727 ) /  0.010545899869065007
            # elif msg.servo >=  -0.26318686746463116  and msg.servo <=  -0.23170159114638744 :
            #     self.servo_pwm = (float(msg.servo) +  0.8823973017234237 ) /  0.01049509210608123
            # elif msg.servo >=  -0.2317015911463911  and msg.servo <=  -0.20405523567075 :
            #     self.servo_pwm = (float(msg.servo) +  0.8030596043096409 ) /  0.009215451825213706
            # elif msg.servo >=  -0.2040552356707508  and msg.servo <=  -0.17535113759800158 :
            #     self.servo_pwm = (float(msg.servo) +  0.8259773605803177 ) /  0.009568032690916413
            # elif msg.servo >=  -0.1753511375980017  and msg.servo <=  -0.14467330043109927 :
            #     self.servo_pwm = (float(msg.servo) +  0.8707154467144568 ) /  0.01022594572230081
            # elif msg.servo >=  -0.14467330043110038  and msg.servo <=  -0.10535383771285411 :
            #     self.servo_pwm = (float(msg.servo) +  1.0752339180962618 ) /  0.013106487572748753
            # elif msg.servo >=  -0.1053538377128499  and msg.servo <=  -0.07256813845887589 :
            #     self.servo_pwm = (float(msg.servo) +  0.9140677526442104 ) /  0.010928566417991357
            # elif msg.servo >=  -0.07256813845887311  and msg.servo <=  -0.03838787670736998 :
            #     self.servo_pwm = (float(msg.servo) +  0.9498615234141183 ) /  0.011393420583834354
            # elif msg.servo >=  -0.03838787670737587  and msg.servo <=  -0.016377541782759297 :
            #     self.servo_pwm = (float(msg.servo) +  0.9188012736920392 ) /  0.011005167462308292
            # elif msg.servo >=  -0.016377541782754523  and msg.servo <=  -0.0008380427195389117 :
            #     self.servo_pwm = (float(msg.servo) +  1.2906164649664262 ) /  0.01553949906321551
            # elif msg.servo >=  -0.0008380427195404105  and msg.servo <=  0.0030116995206450614 :
            #     self.servo_pwm = (float(msg.servo) +  0.32036664865493625 ) /  0.003849742240185492
            # elif msg.servo >=  0.003011699520642064  and msg.servo <=  0.03087814781653364 :
            #     self.servo_pwm = (float(msg.servo) +  0.7772488527643225 ) /  0.009288816098630531
            # elif msg.servo >=  0.030878147816537305  and msg.servo <=  0.06526559598978976 :
            #     self.servo_pwm = (float(msg.servo) +  0.9663578492077834 ) /  0.01146248272441748
            # elif msg.servo >=  0.06526559598979342  and msg.servo <=  0.1044716917844073 :
            #     self.servo_pwm = (float(msg.servo) +  1.1109172778486207 ) /  0.013068698598204602
            # elif msg.servo >=  0.10447169178440507  and msg.servo <=  0.13820382448062407 :
            #     self.servo_pwm = (float(msg.servo) +  0.9412244217983843 ) /  0.011244044232073003
            # elif msg.servo >=  0.1382038244806253  and msg.servo <=  0.1703134232510487 :
            #     self.servo_pwm = (float(msg.servo) +  0.8893033361729284 ) /  0.010703199590141184
            # elif msg.servo >=  0.17031342325104348  and msg.servo <=  0.20929975927400823 :
            #     self.servo_pwm = (float(msg.servo) +  1.116235665506792 ) /  0.012995445340988237
            # elif msg.servo >=  0.209299759274016  and msg.servo <=  0.24595097822757306 :
            #     self.servo_pwm = (float(msg.servo) +  1.0368416851469224 ) /  0.012217072984519005
            # elif msg.servo >=  0.24595097822756506  and msg.servo <=  0.2739384641169089 :
            #     self.servo_pwm = (float(msg.servo) +  0.733611027899473 ) /  0.009329161963114648
            # elif msg.servo >=  0.27393846411691636 :
            #     self.servo_pwm = (float(msg.servo) +  0.5560596126520972 ) /  0.007685167377490866
            if msg.servo >=  0.24396781438941717 :
                self.servo_pwm = (float(msg.servo) +  -0.6187211730321502 ) /  -0.006245889310712218
            elif msg.servo <=  0.24396781438941406  and msg.servo >=  0.2154451419199651 :
                self.servo_pwm = (float(msg.servo) +  -0.8144212637783942 ) /  -0.009507557489816335
            elif msg.servo <=  0.215445141919968  and msg.servo >=  0.19216279578901918 :
                self.servo_pwm = (float(msg.servo) +  -0.704374410669893 ) /  -0.007760782043649604
            elif msg.servo <=  0.19216279578902457  and msg.servo >=  0.17003317666065743 :
                self.servo_pwm = (float(msg.servo) +  -0.6790144166131025 ) /  -0.007376539709455726
            elif msg.servo <=  0.17003317666065343  and msg.servo >=  0.14761156515126062 :
                self.servo_pwm = (float(msg.servo) +  -0.6857302413766886 ) /  -0.007473870503130944
            elif msg.servo <=  0.14761156515125945  and msg.servo >=  0.12968864683298476 :
                self.servo_pwm = (float(msg.servo) +  -0.5777616047898516 ) /  -0.005974306106091558
            elif msg.servo <=  0.12968864683298542  and msg.servo >=  0.10388288612938268 :
                self.servo_pwm = (float(msg.servo) +  -0.7748326644230534 ) /  -0.00860192023453424
            elif msg.servo <=  0.10388288612937902  and msg.servo >=  0.0788549992913039 :
                self.servo_pwm = (float(msg.servo) +  -0.7546079439193332 ) /  -0.008342628946025053
            elif msg.servo <=  0.07885499929130724  and msg.servo >=  0.05516531925878143 :
                self.servo_pwm = (float(msg.servo) +  -0.718476360169502 ) /  -0.007896560010841911
            elif msg.servo <=  0.05516531925877899  and msg.servo >=  0.030517441919448052 :
                self.servo_pwm = (float(msg.servo) +  -0.7453058847600441 ) /  -0.008215959113110299
            elif msg.servo <=  0.030517441919454047  and msg.servo >=  0.008601570925738544 :
                self.servo_pwm = (float(msg.servo) +  -0.6660777007372036 ) /  -0.007305290331238501
            elif msg.servo <=  0.008601570925736435  and msg.servo >=  0.004733325935688204 :
                self.servo_pwm = (float(msg.servo) +  -0.35674362003008 ) /  -0.0038682449900482615
            elif msg.servo <=  0.004733325935688759  and msg.servo >=  -0.0036296349608303524 :
                self.servo_pwm = (float(msg.servo) +  -0.7657627675189297 ) /  -0.00836296089651913
            elif msg.servo <=  -0.0036296349608341827  and msg.servo >=  -0.016905375256274058 :
                self.servo_pwm = (float(msg.servo) +  -0.40349306743265634 ) /  -0.004425246765146636
            elif msg.servo <=  -0.016905375256274002  and msg.servo >=  -0.04239931961214882 :
                self.servo_pwm = (float(msg.servo) +  -0.7904028626797629 ) /  -0.008497981451958283
            elif msg.servo <=  -0.042399319612149045  and msg.servo >=  -0.06666123895258835 :
                self.servo_pwm = (float(msg.servo) +  -0.750156712175536 ) /  -0.008087306446813113
            elif msg.servo <=  -0.0666612389525878  and msg.servo >=  -0.08712360799504626 :
                self.servo_pwm = (float(msg.servo) +  -0.6222385188101781 ) /  -0.006820789680819465
            elif msg.servo <=  -0.08712360799504681  and msg.servo >=  -0.10926583384872612 :
                self.servo_pwm = (float(msg.servo) +  -0.6804735549325027 ) /  -0.007380741951226438
            elif msg.servo <=  -0.10926583384872579  and msg.servo >=  -0.13342783092445865 :
                self.servo_pwm = (float(msg.servo) +  -0.7525120618524108 ) /  -0.008053999025244268
            elif msg.servo <=  -0.13342783092445487  and msg.servo >=  -0.15476284092275028 :
                self.servo_pwm = (float(msg.servo) +  -0.6488558690130434 ) /  -0.007111669999431802
            elif msg.servo <=  -0.15476284092275416  and msg.servo >=  -0.17392452107077327 :
                self.servo_pwm = (float(msg.servo) +  -0.5669937779859677 ) /  -0.006387226716006388
            elif msg.servo <=  -0.17392452107077416  and msg.servo >=  -0.19505609019212078 :
                self.servo_pwm = (float(msg.servo) +  -0.6431628182879614 ) /  -0.007043856373782203
            elif msg.servo <=  -0.19505609019211811  and msg.servo >=  -0.21426460178645013 :
                self.servo_pwm = (float(msg.servo) +  -0.566881536383053 ) /  -0.006402837198110682
            elif msg.servo <=  -0.2142646017864509  and msg.servo >=  -0.23014057657300258 :
                self.servo_pwm = (float(msg.servo) +  -0.43135837286664946 ) /  -0.0052919915955172165
            elif msg.servo <=  -0.23014057657300013 :
                self.servo_pwm = (float(msg.servo) +  -0.7129576917783476 ) /  -0.007544786146810782






            # self.servo_pwm = 81.4 + 89.1*float(msg.servo)
        elif self.sel_car == "NewBARC":
            #     self.servo_pwm = (float(msg.servo) +  -0.32193278464528574 ) /  -0.004654119341458697
            # if msg.servo >=  0.2566846775465117 :
            #     self.servo_pwm = (float(msg.servo) +  -0.6772137645871529 ) /  -0.0072505015007007095
            # elif msg.servo <=  0.25668467754650887  and msg.servo >=  0.23146756582979477 :
            #     self.servo_pwm = (float(msg.servo) +  -0.6223327974388628 ) /  -0.006304277929178517
            # elif msg.servo <=  0.23146756582980016  and msg.servo >=  0.20829424369308602 :
            #     self.servo_pwm = (float(msg.servo) +  -0.7103828899885596 ) /  -0.007724440712238055
            # elif msg.servo <=  0.2082942436930889  and msg.servo >=  0.18468046651630532 :
            #     self.servo_pwm = (float(msg.servo) +  -0.7199260825233992 ) /  -0.00787125905892785
            # elif msg.servo <=  0.18468046651629766  and msg.servo >=  0.1529475905995923 :
            #     self.servo_pwm = (float(msg.servo) +  -0.7241393571002901 ) /  -0.007933218979176359
            # elif msg.servo <=  0.15294759059959273  and msg.servo >=  0.12628127241126386 :
            #     self.servo_pwm = (float(msg.servo) +  -0.792939227119488 ) /  -0.00888877272944299
            # elif msg.servo <=  0.12628127241126985  and msg.servo >=  0.10497656163730706 :
            #     self.servo_pwm = (float(msg.servo) +  -0.6588990417603376 ) /  -0.007101570257987571
            # elif msg.servo <=  0.10497656163730629  and msg.servo >=  0.08214429016307656 :
            #     self.servo_pwm = (float(msg.servo) +  -0.6986156199672782 ) /  -0.007610757158076563
            # elif msg.servo <=  0.08214429016307923  and msg.servo >=  0.05702763786489473 :
            #     self.servo_pwm = (float(msg.servo) +  -0.7602939022140623 ) /  -0.008372217432728186
            # elif msg.servo <=  0.05702763786489684  and msg.servo >=  0.036869070854447794 :
            #     self.servo_pwm = (float(msg.servo) +  -0.6214675141574701 ) /  -0.0067195223368163495
            # elif msg.servo <=  0.03686907085444058  and msg.servo >=  0.0078028366744673505 :
            #     self.servo_pwm = (float(msg.servo) +  -0.8797898620736663 ) /  -0.009688744726657766
            # elif msg.servo <=  0.007802836674472138  and msg.servo >=  0.007246066618238282 :
            #     self.servo_pwm = (float(msg.servo) +  -0.05791214173551918 ) /  -0.0005567700562338561
            # elif msg.servo <=  0.0072460666182367905  and msg.servo >=  0.0010465538152072407 :
            #     self.servo_pwm = (float(msg.servo) +  -0.5714017316939339 ) /  -0.006199512803029638
            # elif msg.servo <=  0.0010465538152094611  and msg.servo >=  -0.010414027483334864 :
            #     self.servo_pwm = (float(msg.servo) +  -0.5282332935482473 ) /  -0.005730290649272151
            # elif msg.servo <=  -0.010414027483335975  and msg.servo >=  -0.03287794221959617 :
            #     self.servo_pwm = (float(msg.servo) +  -0.6934553009194863 ) /  -0.0074879715787534275
            # elif msg.servo <=  -0.03287794221959872  and msg.servo >=  -0.05696110792723241 :
            #     self.servo_pwm = (float(msg.servo) +  -0.7458110823272258 ) /  -0.008027721902544582
            # elif msg.servo <=  -0.05696110792722808  and msg.servo >=  -0.07419607614956403 :
            #     self.servo_pwm = (float(msg.servo) +  -0.5175378328173046 ) /  -0.0057449894074453264
            # elif msg.servo <=  -0.07419607614956558  and msg.servo >=  -0.10402343878170728 :
            #     self.servo_pwm = (float(msg.servo) +  -0.9498767075539637 ) /  -0.009942454210713877
            # elif msg.servo <=  -0.1040234387817085  and msg.servo >=  -0.12676022263258424 :
            #     self.servo_pwm = (float(msg.servo) +  -0.6993429239492363 ) /  -0.007578927950291931
            # elif msg.servo <=  -0.12676022263258357  and msg.servo >=  -0.14476343130612246 :
            #     self.servo_pwm = (float(msg.servo) +  -0.5273563591726613 ) /  -0.006001069557846283
            # elif msg.servo <=  -0.14476343130612335  and msg.servo >=  -0.16352724485132175 :
            #     self.servo_pwm = (float(msg.servo) +  -0.5557522743812868 ) /  -0.006254604515066162
            # elif msg.servo <=  -0.16352724485132186  and msg.servo >=  -0.1874521557128075 :
            #     self.servo_pwm = (float(msg.servo) +  -0.7535943381722943 ) /  -0.007974970287161879
            # elif msg.servo <=  -0.18745215571281282  and msg.servo >=  -0.20082531326732567 :
            #     self.servo_pwm = (float(msg.servo) +  -0.601564140003442 ) /  -0.006686578777256398
            # elif msg.servo <=  -0.2008253132673209  and msg.servo >=  -0.2079742960520491 :
            #     self.servo_pwm = (float(msg.servo) +  -0.65705262090007 ) /  -0.007148982784728257
            # elif msg.servo <=  -0.20797429605204176  and msg.servo >=  -0.2291596853957738 :
            #     self.servo_pwm = (float(msg.servo) +  -0.6465030741451508 ) /  -0.007061796447910683
            # elif msg.servo <=  -0.22915968539578335  and msg.servo >=  -0.25069948491193395 :
            #     self.servo_pwm = (float(msg.servo) +  -0.6611520279384434 ) /  -0.0071799331720502155
            # elif msg.servo <=  -0.2506994849119306 :
            #     self.servo_pwm = (float(msg.servo) +  -0.37048861145868683 ) /  -0.004891244853311948
            if msg.servo >=  0.24396781438941717 :
                self.servo_pwm = (float(msg.servo) +  -0.6187211730321502 ) /  -0.006245889310712218
            elif msg.servo <=  0.24396781438941406  and msg.servo >=  0.2154451419199651 :
                self.servo_pwm = (float(msg.servo) +  -0.8144212637783942 ) /  -0.009507557489816335
            elif msg.servo <=  0.215445141919968  and msg.servo >=  0.19216279578901918 :
                self.servo_pwm = (float(msg.servo) +  -0.704374410669893 ) /  -0.007760782043649604
            elif msg.servo <=  0.19216279578902457  and msg.servo >=  0.17003317666065743 :
                self.servo_pwm = (float(msg.servo) +  -0.6790144166131025 ) /  -0.007376539709455726
            elif msg.servo <=  0.17003317666065343  and msg.servo >=  0.14761156515126062 :
                self.servo_pwm = (float(msg.servo) +  -0.6857302413766886 ) /  -0.007473870503130944
            elif msg.servo <=  0.14761156515125945  and msg.servo >=  0.12968864683298476 :
                self.servo_pwm = (float(msg.servo) +  -0.5777616047898516 ) /  -0.005974306106091558
            elif msg.servo <=  0.12968864683298542  and msg.servo >=  0.10388288612938268 :
                self.servo_pwm = (float(msg.servo) +  -0.7748326644230534 ) /  -0.00860192023453424
            elif msg.servo <=  0.10388288612937902  and msg.servo >=  0.0788549992913039 :
                self.servo_pwm = (float(msg.servo) +  -0.7546079439193332 ) /  -0.008342628946025053
            elif msg.servo <=  0.07885499929130724  and msg.servo >=  0.05516531925878143 :
                self.servo_pwm = (float(msg.servo) +  -0.718476360169502 ) /  -0.007896560010841911
            elif msg.servo <=  0.05516531925877899  and msg.servo >=  0.030517441919448052 :
                self.servo_pwm = (float(msg.servo) +  -0.7453058847600441 ) /  -0.008215959113110299
            elif msg.servo <=  0.030517441919454047  and msg.servo >=  0.008601570925738544 :
                self.servo_pwm = (float(msg.servo) +  -0.6660777007372036 ) /  -0.007305290331238501
            elif msg.servo <=  0.008601570925736435  and msg.servo >=  0.004733325935688204 :
                self.servo_pwm = (float(msg.servo) +  -0.35674362003008 ) /  -0.0038682449900482615
            elif msg.servo <=  0.004733325935688759  and msg.servo >=  -0.0036296349608303524 :
                self.servo_pwm = (float(msg.servo) +  -0.7657627675189297 ) /  -0.00836296089651913
            elif msg.servo <=  -0.0036296349608341827  and msg.servo >=  -0.016905375256274058 :
                self.servo_pwm = (float(msg.servo) +  -0.40349306743265634 ) /  -0.004425246765146636
            elif msg.servo <=  -0.016905375256274002  and msg.servo >=  -0.04239931961214882 :
                self.servo_pwm = (float(msg.servo) +  -0.7904028626797629 ) /  -0.008497981451958283
            elif msg.servo <=  -0.042399319612149045  and msg.servo >=  -0.06666123895258835 :
                self.servo_pwm = (float(msg.servo) +  -0.750156712175536 ) /  -0.008087306446813113
            elif msg.servo <=  -0.0666612389525878  and msg.servo >=  -0.08712360799504626 :
                self.servo_pwm = (float(msg.servo) +  -0.6222385188101781 ) /  -0.006820789680819465
            elif msg.servo <=  -0.08712360799504681  and msg.servo >=  -0.10926583384872612 :
                self.servo_pwm = (float(msg.servo) +  -0.6804735549325027 ) /  -0.007380741951226438
            elif msg.servo <=  -0.10926583384872579  and msg.servo >=  -0.13342783092445865 :
                self.servo_pwm = (float(msg.servo) +  -0.7525120618524108 ) /  -0.008053999025244268
            elif msg.servo <=  -0.13342783092445487  and msg.servo >=  -0.15476284092275028 :
                self.servo_pwm = (float(msg.servo) +  -0.6488558690130434 ) /  -0.007111669999431802
            elif msg.servo <=  -0.15476284092275416  and msg.servo >=  -0.17392452107077327 :
                self.servo_pwm = (float(msg.servo) +  -0.5669937779859677 ) /  -0.006387226716006388
            elif msg.servo <=  -0.17392452107077416  and msg.servo >=  -0.19505609019212078 :
                self.servo_pwm = (float(msg.servo) +  -0.6431628182879614 ) /  -0.007043856373782203
            elif msg.servo <=  -0.19505609019211811  and msg.servo >=  -0.21426460178645013 :
                self.servo_pwm = (float(msg.servo) +  -0.566881536383053 ) /  -0.006402837198110682
            elif msg.servo <=  -0.2142646017864509  and msg.servo >=  -0.23014057657300258 :
                self.servo_pwm = (float(msg.servo) +  -0.43135837286664946 ) /  -0.0052919915955172165
            elif msg.servo <=  -0.23014057657300013 :
                self.servo_pwm = (float(msg.servo) +  -0.7129576917783476 ) /  -0.007544786146810782








            # if msg.servo >= 0:
            #     self.servo_pwm = (float(msg.servo) ) / 0.00822442841151 + 83.3
            # else:
            #     self.servo_pwm = (float(msg.servo) ) / 0.00890579042074 + 83.3
            # Old Map
            # self.servo_pwm = 83.3 + 103.1*float(msg.servo)

        # compute motor command
        FxR = float(msg.motor)
        if FxR == 0:
            self.motor_pwm = 90.0
        elif FxR > 0:
            #self.motor_pwm = max(94,91 + 6.5*FxR)   # using writeMicroseconds() in Arduino
            self.motor_pwm = 91 + 6.5*FxR   # using writeMicroseconds() in Arduino

            # self.motor_pwm = max(94,90.74 + 6.17*FxR)
            #self.motor_pwm = 90.74 + 6.17*FxR
            
            #self.motor_pwm = max(94,90.12 + 5.24*FxR)
            #self.motor_pwm = 90.12 + 5.24*FxR
            # Note: Barc doesn't move for u_pwm < 93
        else:               # motor break / slow down
            self.motor_pwm = 93.5 + 46.73*FxR
            # self.motor_pwm = 98.65 + 67.11*FxR
            #self.motor = 69.95 + 68.49*FxR
            
        self.update_arduino()

    def neutralize(self):
        self.motor_pwm = 40             # slow down first
        self.servo_pwm = 90
        self.update_arduino()
        rospy.sleep(1)                  # slow down for 1 sec
        self.motor_pwm = 90
        self.update_arduino()
    def update_arduino(self):
        self.ecu_cmd.header.stamp = get_rostime()
        self.ecu_cmd.motor = self.motor_pwm
        self.ecu_cmd.servo = self.servo_pwm
        self.ecu_pub.publish(self.ecu_cmd)

def arduino_interface():
    # launch node, subscribe to motorPWM and servoPWM, publish ecu
    init_node('arduino_interface')
    llc = low_level_control()

    Subscriber('ecu', ECU, llc.pwm_converter_callback, queue_size = 1)
    Subscriber('srv_fbk', ECU, llc.fbk_servo_callback, queue_size = 1)
    llc.ecu_pub = Publisher('ecu_pwm', ECU, queue_size = 1)

    # Set motor to neutral on shutdown
    on_shutdown(llc.neutralize)

    # process callbacks and keep alive
    spin()

class SteeringPID(object):

    def __init__(self, loop_rate):

        self.Ts       = 1/loop_rate
        self.Steering = 0.0
        self.integral = 0.0

    def solve(self, comanded_delta, measured_delta):
        """Computes control action
        Arguments:
            delta: current steering angle
        """
        error = comanded_delta - measured_delta
        #print error, "\n"
        self.integral = self.integral +  error*self.Ts
        self.integral = self.truncate( self.integral , 3 )

        self.Steering =  self.truncate(self.Steering + 0.02*error + 0.006*self.integral ,  0.3)
        

    def truncate(self, val, bound):
        return np.maximum(-bound, np.minimum(val, bound))
        
#############################################################
if __name__ == '__main__':
    try:
        arduino_interface()
    except ROSInterruptException:
        pass
