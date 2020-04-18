package com.n9mtq4.hdr2sdrlut

import java.io.File

/**
 * Created by will on 4/17/20 at 9:49 PM.
 *
 * @author Will "n9Mtq4" Bresnahan
 */

private fun Double.format(digits: Int) = "%.${digits}f".format(this)

private fun Double.mix(newValue: Double, newSampleCount: Long): Double {
	
	val delta = (newValue - this) / newSampleCount
	return this + delta
	
}

class LutGen(val size: Int, val maxSamples: Long = 10_000_000L) {
	
	val table = Array(size) { Array(size) { Array(size) { DoubleArray(3) { 0.0 } } } }
	val denom = Array(size) { Array(size) { Array(size) { 0L } } }
	
	fun updateAverage(ri: Int, gi: Int, bi: Int, updateRGB: DoubleArray) {
		
		val (ur, ug, ub) = updateRGB
		
		val (or, og, ob) = table[ri][gi][bi]
		
		if (denom[ri][gi][bi] >= maxSamples) return
		val newSampleCount = ++denom[ri][gi][bi]
		
		table[ri][gi][bi][0] = or.mix(ur, newSampleCount)
		table[ri][gi][bi][1] = og.mix(ug, newSampleCount)
		table[ri][gi][bi][2] = ob.mix(ub, newSampleCount)
		
	}
	
	fun write(filePath: String) {
		
		val file = File(filePath)
		file.bufferedWriter().use { writer ->
			
			writer.write("TITLE \"HDR_2_SDR_generated_lut\"")
			writer.newLine()
			writer.write("LUT_3D_SIZE $size")
			writer.newLine()
			
			for (bi in 0 until size) {
				for (gi in 0 until size) {
					for (ri in 0 until size) {
						
						val (lr, lg, lb) = table[ri][gi][bi]
						writer.write("${lr.format(6)} ${lg.format(6)} ${lb.format(6)}")
						writer.newLine()
						
					}
				}
			}
			
		}
		
	}
	
}
