package com.n9mtq4.hdr2sdrlut

import java.awt.image.BufferedImage
import java.io.BufferedWriter
import java.io.File
import javax.imageio.ImageIO
import kotlin.math.roundToInt

/**
 * Created by will on 3/30/20 at 7:59 AM.
 *
 * @author Will "n9Mtq4" Bresnahan
 */

const val HDR_FRAMES_DIR = "/mnt/L4/media/clonewars/Season07/hdrluts/1080hdr"
const val SDR_FRAMES_DIR = "/mnt/L4/media/clonewars/Season07/hdrluts/1080"

const val CSV_SPLITS = 4

const val X_BLACK_BAR = 0
const val Y_BLACK_BAR = 132

const val SDR_START = 2
const val SDR_END = 30810 + 200

const val HDR_START = 74
const val HDR_END = 30882 + 200

const val FRAME_SELECTION = 1
const val X_SELECTION = 8 / (CSV_SPLITS / 2)
const val Y_SELECTION = 6 / (CSV_SPLITS / 2)

val X_RANDOM_RANGE = 0 until X_SELECTION
val Y_RANDOM_RANGE = 0 until Y_SELECTION

fun main() {
	
//	generatePyImageMap()
//	generateCSV()
	genLut()
	
}

fun getFileMap(): List<Pair<File, File>> {
	
	val hdrFiles = File(HDR_FRAMES_DIR).listFiles()!!.sorted().subList(HDR_START - 1, HDR_END)
	val sdrFiles = File(SDR_FRAMES_DIR).listFiles()!!.sorted().subList(SDR_START - 1, SDR_END)
	
	assert(hdrFiles.size == sdrFiles.size)
	
	val fileMap = sdrFiles
		.zip(hdrFiles)
		.filterIndexed { i, _ -> i % FRAME_SELECTION == 0 }
	
	return fileMap
	
}

fun genLut() {
	
	val lut = LutGen(33)
	
	val fileMap = getFileMap()
	
	fileMap
		.shuffled()
		.asSequence()
		.map { (sdrFile, hdrFile) -> ImageIO.read(sdrFile) to ImageIO.read(hdrFile) }
		.forEachIndexed { index, (sdrImage, hdrImage) ->
			println("processing ${index + 1}/${fileMap.size}")
			lutProcessImage(lut, sdrImage, hdrImage)
		}
	
	lut.write("direct_lut.cube")
	
}

fun lutProcessImage(lut: LutGen, sdrImage: BufferedImage, hdrImage: BufferedImage) {
	
	assert(sdrImage.width == hdrImage.width)
	assert(sdrImage.height == hdrImage.height)
	
	val height = sdrImage.height - Y_BLACK_BAR
	val width = sdrImage.width - X_BLACK_BAR
	
	for (y in Y_BLACK_BAR until height step 1) { // step Y_SELECTION
		for (x in X_BLACK_BAR until width step 1) { // step X_SELECTION
			
			lutProcessPixel(lut, sdrImage, hdrImage, x, y)
			
		}
	}
	
}

fun lutProcessPixel(lut: LutGen, sdrImage: BufferedImage, hdrImage: BufferedImage, x: Int, y: Int) {
	
	val sdrPixel = sdrImage.raster.getPixel(x, y, IntArray(3))
	val hdrPixel = hdrImage.raster.getPixel(x, y, IntArray(3))
	
	// convert sdr pixel to lut vector
	val sdrLutVector = sdrPixel.map { it / 255.0 }.toDoubleArray()
	
	// convert hdr pixel to nearest neighbor in lut
	val (lir, lig, lib) = hdrPixel.map { ((it / 65535.0) * lut.size).roundToInt() }
	
	// update that index in the lut
	lut.updateAverage(lir, lig, lib, sdrLutVector)
	
}

fun generateCSV() {
	
	val fileMap = getFileMap()
	
	val data = fileMap
		.shuffled()
		.asSequence()
		.map { (sdrFile, hdrFile) -> ImageIO.read(sdrFile) to ImageIO.read(hdrFile) }
		.mapIndexed { index, (sdrImage, hdrImage) ->
			println("processing ${index + 1}/${fileMap.size}")
			csvProcessImage(sdrImage, hdrImage)
		}.flatten()
	
	val outputFiles = Array(CSV_SPLITS) { i -> File("s07e05_${i + 1}.csv") }
	val outputWriters = outputFiles.map { it.bufferedWriter() }
	val lineCounters = Array(CSV_SPLITS) { 0L }
	
	outputWriters.forEach { writer -> 
		writer.write("hr,hg,hb,sr,sg,sb")
		writer.newLine()
	}
	
	data.chunked(CSV_SPLITS).forEach { chunk -> 
		
		assert(chunk.size == outputFiles.size)
		
		chunk.forEachIndexed { index, entry -> 
			val strLine = entry.joinToString(separator = ",")
			outputWriters[index].write(strLine)
			outputWriters[index].newLine()
			lineCounters[index]++
		}
		
	}
	
	outputWriters.forEach(BufferedWriter::close)
	
	println("Row stats: ${lineCounters.contentToString()}")
	
}

fun generatePyImageMap() {
	
	val fileMap = getFileMap()
	
	val outputFile = File("pyfilemap.txt")
	val outputWriter = outputFile.bufferedWriter()
	
	fileMap.map { (s, h) -> s.absolutePath to h.absolutePath }
		.forEach { (sdrFile, hdrFile) ->
		outputWriter.write(hdrFile)
		outputWriter.newLine()
		outputWriter.write(sdrFile)
		outputWriter.newLine()
	}
	
	outputWriter.close()
	
}

fun csvProcessImage(sdrImage: BufferedImage, hdrImage: BufferedImage): List<List<String>> {
	
	assert(sdrImage.width == hdrImage.width)
	assert(sdrImage.height == hdrImage.height)
	
	val height = sdrImage.height - Y_BLACK_BAR
	val width = sdrImage.width - X_BLACK_BAR
	
	return (Y_BLACK_BAR until height step Y_SELECTION).map { y ->
		(X_BLACK_BAR until width step X_SELECTION).map { x ->
			val xOffset = X_RANDOM_RANGE.random()
			val yOffset = Y_RANDOM_RANGE.random()
			val cx = (x + xOffset).coerceIn(0, width)
			val cy = (y + yOffset).coerceIn(0, height)
			csvLinePixel(sdrImage, hdrImage, cx, cy)
		}
	}.flatten()
	
}

fun csvLinePixel(sdrImage: BufferedImage, hdrImage: BufferedImage, sdrx: Int, sdry: Int): List<String> {
	
	val sdrPixel = sdrImage.raster.getPixel(sdrx, sdry, IntArray(3))
	val hdrPixel = hdrImage.raster.getPixel(sdrx, sdry, IntArray(3))
	
	return (hdrPixel + sdrPixel).map { it.toString() }
	
}
