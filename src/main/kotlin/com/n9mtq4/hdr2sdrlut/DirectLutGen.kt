package com.n9mtq4.hdr2sdrlut

/**
 * Created by will on 4/17/20 at 9:49 PM.
 *
 * @author Will "n9Mtq4" Bresnahan
 */

private fun Double.mix(newValue: Double, newSampleCount: Long): Double {
	
	val delta = (newValue - this) / newSampleCount
	return this + delta
	
}

class LutGen(size: Int, val maxSamples: Long = 10_000_000L) : Lut(size) {
	
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
	
	/**
	 * Merges another lut into this one. Replaces any pixels
	 * that weren't sampled in this lut with the values from otherLut
	 * */
	fun merge(otherLut: Lut) {
		
		assert(this.size == otherLut.size)
		
		for (ri in 0 until size) {
			for (gi in 0 until size) {
				for (bi in 0 until size) {
					
					if (denom[ri][gi][bi] > 0) continue
					
					// this pixel was never sampled
					table[ri][gi][bi] = otherLut.table[ri][gi][bi]
					
				}
			}
		}
		
	}
	
}
