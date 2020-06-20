/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import java.util.Random

import scala.math.exp

import breeze.linalg.{Vector, DenseVector, squaredDistance}

import org.apache.spark._
import org.apache.spark.deploy.SparkHadoopUtil
import org.apache.spark.scheduler.InputFormatInfo


/**
 * Linear regression based classification.
 * 
 */
object SparkLinearRegression {
  val D = 111   // Numer of dimensions
  val rand = new Random(42)

  case class DataPoint(x: Vector[Double], y: Double)
  //data point parsing
  def parsePoint(line: String): DataPoint = {
    val tok = new java.util.StringTokenizer(line, " ")
    var y = tok.nextToken.toDouble
    var x = new Array[Double](D)
    var i = 0
    var bound = D
    while (i < D) {
      if(tok.hasMoreTokens()){
      val point = tok.nextToken().toString()
      val div = new java.util.StringTokenizer(point, ":")
      val index = div.nextToken().toInt -1 
      val value = div.nextToken().toDouble
      x(index) = value
      bound = index
      }else bound = D
      while (i < bound){
          x(i) = 0; i+=1
      }
      i = bound + 1
    } 
    DataPoint(new DenseVector(x), y)
  }

  def main(args: Array[String]) {
    val rootpath="hdfs://ip:9000/home"
    if (args.length < 2) {
      System.err.println("Usage: LR <trainfile> <testfile>")
      System.exit(1)
    }
    var threshold = 10000.0
    val sparkConf = new SparkConf().setAppName("LinearRegression")
    val trainfilePath = rootpath + args(0)
    val testfilePath = rootpath + args(1)
    val conf = SparkHadoopUtil.get.newConfiguration()
    val sc = new SparkContext(sparkConf)
    val traindata = sc.textFile(trainfilePath)
    val points = traindata.map(parsePoint _).cache()
    val testdata = sc.textFile(testfilePath)
    val testpoints = testdata.map(parsePoint _).cache()
    var w = DenseVector.fill(D){0.0}
     println("Initial w: " + w)
    var fw = w
    var oldoff=Double.MaxValue
    var dv = -1.0
    val maxy = points.map { p => p.y }.max()
    val Num = points.count()
    // alpha calculation
    var alpha = (1.0 / (maxy * Num * D * 0.18 )) 
    var i=1
    var off=0.0 
    // main iteration
    while( (dv < 0 || i< 30) && i < 100)
    {
      println("On iteration " + i)
      val gradient = points.map { p =>
        p.x * ((w.dot(p.x)) - p.y)
      }.reduce(_ + _)
      println("gradient:" + gradient)
      val costs = points.map { p =>
         (w.dot(p.x) - p.y) * (w.dot(p.x) - p.y)
      }
      // square loss
      val offset = points.map { p =>
         (w.dot(p.x) - p.y) * (w.dot(p.x) - p.y)
      }.reduce(_ + _)
      val offmax = costs.max()
      val offmin = costs.min()
      // W update
      w -= gradient * alpha
      println("---------w:" + w)
      println("Max Y: "+ maxy)
      off = math.sqrt(offset) * 1.0 / Num
      dv = off - oldoff
      if(off < oldoff){
        println("********************************************************")
      }
      println("devia:"+ off)
      println("max devia:"+math.sqrt(offmax))
      println("min devia:"+math.sqrt(offmin))
      oldoff = off
      i+=1
    }
    println("###########################################################")
    println("Final w: " + w)
    while(threshold <= 100000.0){
    val correctNum = testpoints.map{ p => 
       if ( w.dot(p.x) >= threshold && p.y >= threshold
           || w.dot(p.x) < threshold && p.y < threshold) 
         1 else 0
    }.reduce(_ + _)
    val totalNum = testpoints.count()
    println("Threshold:" + threshold)
    println("Prediction accuracy:" + 1.0 * correctNum / totalNum)
    threshold  =  threshold + 10000.0
    }
    sc.stop()
  }
}
