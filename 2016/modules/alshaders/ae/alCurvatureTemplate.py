import pymel.core as pm
from alShaders import *

class AEalCurvatureTemplate(alShadersTemplate):
	controls = {}
	params = {}
	def setup(self):
		self.params.clear()
		self.params["mode"] = Param("mode", "Mode", "Select the type of curvature to output. positive selects convex regions while negative selects concave regions.", "enum", presets=None)
		self.params["samples"] = Param("samples", "Samples", "The sampling rate for the curvature calculation.", "int", presets=None)
		self.params["sampleRadius"] = Param("sampleRadius", "Radius", "The radius to consider when estimating the curvature. Smaller values pick out finer detail, while larger values give a smoother result.", "float", presets=None)
		self.params["traceSet"] = Param("traceSet", "Trace set", "Enter a trace set here to restrict the curvature calculation to only consider that set of objects.", "string", presets=None)
		self.params["RMPinputMin"] = Param("RMPinputMin", "Input min", "Sets the minimum input value. Use this to pull values outside of 0-1 into a 0-1 range.", "float", presets=None)
		self.params["RMPinputMax"] = Param("RMPinputMax", "Input max", "Sets the maximum input value. Use this to pull values outside of 0-1 into a 0-1 range.", "float", presets=None)
		self.params["RMPcontrast"] = Param("RMPcontrast", "Contrast", "Scales the contrast of the input signal.", "float", presets=None)
		self.params["RMPcontrastPivot"] = Param("RMPcontrastPivot", "Pivot", "Sets the pivot point around which the input signal is contrasted.", "float", presets=None)
		self.params["RMPbias"] = Param("RMPbias", "Bias", "Bias the signal higher or lower. Values less than 0.5 push the average lower, values higher than 0.5 push it higher.", "float", presets=None)
		self.params["RMPgain"] = Param("RMPgain", "Gain", "Adds gain to the signal, in effect a different form of contrast. Values less than 0.5 increase the gain, values greater than 0.5 decrease it.", "float", presets=None)
		self.params["RMPoutputMin"] = Param("RMPoutputMin", "Output min", "Sets the minimum value of the output. Use this to scale a 0-1 signal to a new range.", "float", presets=None)
		self.params["RMPoutputMax"] = Param("RMPoutputMax", "Output max", "Sets the maximum value of the output. Use this to scale a 0-1 signal to a new range.", "float", presets=None)
		self.params["RMPclampEnable"] = Param("RMPclampEnable", "Enable", "When enabled, will clamp the output to Min-Max.", "bool", presets=None)
		self.params["RMPthreshold"] = Param("RMPthreshold", "Expand", "When enabled, will expand the clamped range to 0-1 after clamping.", "bool", presets=None)
		self.params["RMPclampMin"] = Param("RMPclampMin", "Min", "Minimum value to clamp to.", "float", presets=None)
		self.params["RMPclampMax"] = Param("RMPclampMax", "Max", "Maximum value to clamp to.", "float", presets=None)

		self.addSwatch()
		self.beginScrollLayout()

		self.addControl("mode", label="Mode", annotation="Select the type of curvature to output. positive selects convex regions while negative selects concave regions.")
		self.addControl("samples", label="Samples", annotation="The sampling rate for the curvature calculation.")
		self.addCustomFlt("sampleRadius")
		self.addControl("traceSet", label="Trace set", annotation="Enter a trace set here to restrict the curvature calculation to only consider that set of objects.")
		self.beginLayout("Remap", collapse=True)
		self.addCustomFlt("RMPinputMin")
		self.addCustomFlt("RMPinputMax")
		self.beginLayout("Contrast", collapse=False)
		self.addCustomFlt("RMPcontrast")
		self.addCustomFlt("RMPcontrastPivot")
		self.endLayout() # END Contrast
		self.beginLayout("Bias and gain", collapse=False)
		self.addCustomFlt("RMPbias")
		self.addCustomFlt("RMPgain")
		self.endLayout() # END Bias and gain
		self.addCustomFlt("RMPoutputMin")
		self.addCustomFlt("RMPoutputMax")
		self.beginLayout("Clamp", collapse=False)
		self.addControl("RMPclampEnable", label="Enable", annotation="When enabled, will clamp the output to Min-Max.")
		self.addControl("RMPthreshold", label="Expand", annotation="When enabled, will expand the clamped range to 0-1 after clamping.")
		self.addCustomFlt("RMPclampMin")
		self.addCustomFlt("RMPclampMax")
		self.endLayout() # END Clamp
		self.endLayout() # END Remap

		pm.mel.AEdependNodeTemplate(self.nodeName)
		self.addExtraControls()

		self.endScrollLayout()
