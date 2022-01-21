#! /usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from visual import *
except:
    print("Module python-visual manquant.")
    exit(0)
from select import select
import os, sys, time, traceback, string, random
import logging, getopt, socket
import dbus, dbus.glib, dbus.mainloop.glib, dbus.service, gobject
import _thread
from . import povexport
import struct, re


log = logging.getLogger("rtgraph3d")
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(levelname)-5s: %(message)s"))
log.addHandler(console_handler)
log.setLevel(20)


DT = 0.1  # time interval
ACCEL = 5


class python_physics_engine:
    C_ENGINE = 0
    FRICTION = -0.5
    MIN_DIST = 16

    @staticmethod
    def add_edge(e1, e2):
        pass

    @staticmethod
    def update(the_world, pos, spd, changed, dt, ATTRACT, REPULS):
        ln = len(pos)
        for o in the_world.lst:
            o.F = python_physics_engine.FRICTION * o.V
        i = 0
        while i < the_world.world_len:
            o = the_world.lst[i]
            i += 1
            j = i
            while j < the_world.world_len:
                n = the_world.lst[j]
                j += 1
                d = n.pos - o.pos
                if n in o.edges:
                    F = d * ATTRACT
                    o.F += F
                    n.F -= F

                l = d.mag2
                l = l ** 2
                if l < python_physics_engine.MIN_DIST:
                    l = python_physics_engine.MIN_DIST
                F = -REPULS * d / l
                o.F += F
                n.F -= F
        for o in the_world.lst:
            dV = o.F * dt
            o.V += dV
            o.pos += (dV / 2 + o.V) * dt


def get_physics_engine(mode=0):  # 0:auto, 1:force python, 2: force C only, 3: force SSE
    if mode != 1:
        try:
            import PyInline
        except ImportError:
            log.warning("PyInline module not found! Fallback to Python physics engine")
            mode = 1

    if mode == 0:
        try:
            mode = 2

            test_sse = PyInline.build(
                language="C",
                code=r"""
            int test_sse(void)
            {
                    int sse_support;
                    asm("push %%ebx \n\t"  /* do not clobber PIC register */
                        "mov $1, %%eax \n\t"
                        "cpuid \n\t"
                        "xor %%eax,%%eax \n\t"
                        "test $0x02000000, %%edx \n\t" /* Test SSE presence */
                        "jz end \n\t"
                        "inc %%eax \n\t"
                        "test $0x04000000, %%edx \n\t" /* Test SSE2 presence */
                        "jz end \n\t"
                        "inc %%eax \n\t"
                        "end: \n\t"
                        "pop %%ebx \n\t"
                        : "=a"(sse_support) );
                    return sse_support;
            }""",
            )
            sse_support = test_sse.test_sse()
            if sse_support > 0:
                mode = 3
                log.info("Detected SSE%s compatible CPU" % ["?", "", "2"][sse_support])
            else:
                log.info("Did not detect any SSE compatible CPU")
                mode = 2
        except:
            log.warning("x86 SSE test failed. Fallback to C physics engine")
            mode = 2

    log.info("Using %s physics engine" % ["??", "Python", "C", "C+SSE"][mode])
    if mode == 1:
        log.warning("Python physics engine is 25 to 1000 times slower")

    if mode >= 2:
        sse_code = r"""
#define MAXPTS 2000
#define MIN_DIST 16
#define MAX_DIST 10
#define FRICTION -0.5
#define ACCEL 1
#define CN 4

#ifndef USE_SSE  /********[ C ONLY ]********/

float force[CN*MAXPTS];

PyFloatObject *pf_coord[CN*MAXPTS];
PyFloatObject *pf_speed[CN*MAXPTS];
PyObject *pt_coord[MAXPTS];
PyObject *pt_speed[MAXPTS];

#define PTC(i) pt_coord[i]
#define PTS(i) pt_speed[i]

#define X(i) (PFX(i)->ob_fval)
#define Y(i) (PFY(i)->ob_fval)
#define Z(i) (PFZ(i)->ob_fval)
#define C(i) (PF(i)->ob_fval)
#define PFX(i) pf_coord[CN*i]
#define PFY(i) pf_coord[CN*i+1]
#define PFZ(i) pf_coord[CN*i+2]
#define PF(i) pf_coord[i]

#define SX(i) (PFSX(i)->ob_fval)
#define SY(i) (PFSY(i)->ob_fval)
#define SZ(i) (PFSZ(i)->ob_fval)
#define S(i) (PFS(i)->ob_fval)
#define PFSX(i) pf_speed[CN*i]
#define PFSY(i) pf_speed[CN*i+1]
#define PFSZ(i) pf_speed[CN*i+2]
#define PFS(i) pf_speed[i]

#define FX(i) force[CN*i]
#define FY(i) force[CN*i+1]
#define FZ(i) force[CN*i+2]
#define F(i) force[i]

#else         /********[ C + SSE ]********/


#define NEEDED_PTS (MAXPTS+4)

float coordx[NEEDED_PTS];
float coordy[NEEDED_PTS];
float coordz[NEEDED_PTS];
float speedx[NEEDED_PTS];
float speedy[NEEDED_PTS];
float speedz[NEEDED_PTS];
float forcex[NEEDED_PTS];
float forcey[NEEDED_PTS];
float forcez[NEEDED_PTS];

PyFloatObject *pf_coordx[MAXPTS];
PyFloatObject *pf_coordy[MAXPTS];
PyFloatObject *pf_coordz[MAXPTS];
PyFloatObject *pf_speedx[MAXPTS];
PyFloatObject *pf_speedy[MAXPTS];
PyFloatObject *pf_speedz[MAXPTS];

PyObject *pt_coord[MAXPTS];
PyObject *pt_speed[MAXPTS];

#define PTC(i) pt_coord[i]
#define PTS(i) pt_speed[i]

#define X(i) (coordx[i])
#define Y(i) (coordy[i])
#define Z(i) (coordz[i])

#define PX(i) (PFX(i)->ob_fval)
#define PY(i) (PFY(i)->ob_fval)
#define PZ(i) (PFZ(i)->ob_fval)
#define PFX(i) pf_coordx[i]
#define PFY(i) pf_coordy[i]
#define PFZ(i) pf_coordz[i]

#define SX(i) (speedx[i])
#define SY(i) (speedy[i])
#define SZ(i) (speedz[i])

#define PSX(i) (PFSX(i)->ob_fval)
#define PSY(i) (PFSY(i)->ob_fval)
#define PSZ(i) (PFSZ(i)->ob_fval)
#define PFSX(i) pf_speedx[i]
#define PFSY(i) pf_speedy[i]
#define PFSZ(i) pf_speedz[i]

#define FX(i) forcex[i]
#define FY(i) forcey[i]
#define FZ(i) forcez[i]

#define CONDADD(idx, len, arr) do{ switch (len-idx) { default: (arr)[2] += (arr)[3]; case 3: (arr)[1] += (arr)[2]; case 2: (arr)[0] += (arr)[1]; case 1:; } } while(0);

int mmx_control_flags = 0x5f80; // 0x5fc0; // set FTZ and DAZ

float tmpshow[4] __attribute__ ((aligned(32)));
#define SHOW(r,fmt,args ...) do { __asm__("lea tmpshow,%%edx \n\t movaps " r ",(%%edx) \n\t":::"edx"); \
          printf("[%+.3f %+.3f %+.3f %+.3f] " fmt "\n" , tmpshow[0],tmpshow[1],tmpshow[2],tmpshow[3], ## args );} while(0)

#endif /**********************************/

#define LOG(x ...)
//#define LOG(x ...) printf(x)

int old_len;


#define EDGEW1 16
#define EDGELW1 4
#define EDGEW2 16
#define EDGELW2 4
#define EDGEW3 (8*sizeof(int))
#define EDGELW3 5

struct edge_part2 {
    int val[EDGEW2];
};

struct edge_part1 {
    struct edge_part2 *next[EDGEW1];
};


struct edge_part1 *edges[MAXPTS];

// we always have i <= j
int check_edge(int i, int j)
{
        struct edge_part1 *p1;
        struct edge_part2 *p2;
        int n1,n2,n3;

        p1 = edges[i];
        if (!p1) return 0;

        n1 = (j >> (2*EDGELW1)) & (EDGEW1-1);
        p2 = p1->next[n1];
        if (!p2) return 0;

        n2 = (j >> EDGELW2) & (EDGEW2-1);
        n3 = j & (EDGEW3-1);

        return (p2->val[n2] & (1<<n3)) != 0;
}

void do_add_edge(int i, int j)
{
        struct edge_part1 *p1;
        struct edge_part2 *p2;
        int n1,n2,n3;

        n1 = (j >> (2*EDGELW1)) & (EDGEW1-1);
        n2 = (j >> EDGELW2) & (EDGEW2-1);
        n3 = j & (EDGEW3-1);

        p1 = edges[i];
        if (!p1) {
                p1 = edges[i] = malloc(sizeof(struct edge_part1));
                bzero(p1, sizeof(struct edge_part1));
        }
        p2 = p1->next[n1];
        if (!p2) {
                p2 = p1->next[n1] = malloc(sizeof(struct edge_part2));
                bzero(p2, sizeof(struct edge_part2));
        }
        p2->val[n2] |= 1<<n3;
}


void add_edge(int i, int j)
{
      if (i < j) { do_add_edge(i,j); } // check is always called with i < j
      else { do_add_edge(j,i); }
}


#ifdef USE_SSE   /********[ C + SSE ]********/
// SSE prepa

float attract[4] __attribute__ ((aligned(32)));
float repuls[4] __attribute__ ((aligned(32)));
float min_dist[4] __attribute__ ((aligned(32))) = { MIN_DIST, MIN_DIST, MIN_DIST, MIN_DIST };
float friction[4] __attribute__ ((aligned(32))) = { FRICTION, FRICTION, FRICTION };
float zero[4] __attribute__ ((aligned(32))) = { 0.0, 0.0, 0.0, 0.0 };
float half[4] __attribute__ ((aligned(32))) = { 0.5, 0.5, 0.5, 0.5 };
float tmpsse1[4] __attribute__ ((aligned(32)));
float tmpsse2[4] __attribute__ ((aligned(32)));
float tmpsse3[4] __attribute__ ((aligned(32)));

#endif           /***************************/


float update(PyObject *the_world, PyObject *pos, PyObject *spd, int changed, float dt, float ATTRACT, float REPULS)
{
	PyObject *item;
	int i,j,len;
        float dA;
#ifndef USE_SSE
        float a,D,DD,dX,dY,dZ;
#endif


	len = PyList_GET_SIZE(pos);
	if (len > MAXPTS) len = MAXPTS;
#ifdef USE_SSE
        repuls[0] = repuls[1] = repuls[2] = repuls[3] = REPULS;

        LOG("=== changed=%i old_len=%04i len=%04i attract=%+.f repuls=%+.2f\n",
               changed, old_len, len, ATTRACT, REPULS);
#endif

        if (changed  || (old_len != len)) {
                for (i=old_len; i<len; i++) {
                        PFX(i)  = (PyFloatObject *)PyFloat_FromDouble(0.0);
                        PFY(i)  = (PyFloatObject *)PyFloat_FromDouble(0.0);
                        PFZ(i)  = (PyFloatObject *)PyFloat_FromDouble(0.0);
                        PTC(i) = item = PyTuple_New(3);
                        PyTuple_SET_ITEM(item, 0, (PyObject *)PFX(i));
                        PyTuple_SET_ITEM(item, 1, (PyObject *)PFY(i));
                        PyTuple_SET_ITEM(item, 2, (PyObject *)PFZ(i));

                        PFSX(i) = (PyFloatObject *)PyFloat_FromDouble(0.0);
                        PFSY(i) = (PyFloatObject *)PyFloat_FromDouble(0.0);
                        PFSZ(i) = (PyFloatObject *)PyFloat_FromDouble(0.0);
                        PTS(i) = item = PyTuple_New(3);
                        PyTuple_SET_ITEM(item, 0, (PyObject *)PFSX(i));
                        PyTuple_SET_ITEM(item, 1, (PyObject *)PFSY(i));
                        PyTuple_SET_ITEM(item, 2, (PyObject *)PFSZ(i));
                }
                old_len = len;
	    	for (i=0; i<len; i++) {
                        item = PyList_GET_ITEM(pos, i);
                        if (PTC(i) != item) {
                                X(i) = ((PyFloatObject *)PyTuple_GET_ITEM(item, 0))->ob_fval;
                                Y(i) = ((PyFloatObject *)PyTuple_GET_ITEM(item, 1))->ob_fval;
                                Z(i) = ((PyFloatObject *)PyTuple_GET_ITEM(item, 2))->ob_fval;
                                Py_INCREF(PTC(i));
                                PyList_SET_ITEM(pos, i, PTC(i));
                        }

                        item = PyList_GET_ITEM(spd, i);
                        if (PTS(i) != item) {
                                SX(i) = ((PyFloatObject *)PyTuple_GET_ITEM(item, 0))->ob_fval;
                                SY(i) = ((PyFloatObject *)PyTuple_GET_ITEM(item, 1))->ob_fval;
                                SZ(i) = ((PyFloatObject *)PyTuple_GET_ITEM(item, 2))->ob_fval;
                                Py_INCREF(PTS(i));
                                PyList_SET_ITEM(spd, i, PTS(i));
                        }

	    	}
        }


#ifndef USE_SSE    /********[ C ONLY ]********/
        bzero(force, sizeof(float)*CN*len);
#else             /********[ C + SSE ]********/
        asm("ldmxcsr %0 \n\t" :: "m"(mmx_control_flags)); // set DAZ and MTZ into MMX control reg

        asm("movaps %0, %%xmm0 \n\t" ::"m"(friction[0]));
	for (i=0; i<len; i+=4) {
                asm("movups %0, %%xmm1"::"m"(SX(i)));
                asm("movups %0, %%xmm2"::"m"(SY(i)));
                asm("movups %0, %%xmm3"::"m"(SZ(i)));
                asm("mulps %%xmm0, %%xmm1 \n\t"
                    "mulps %%xmm0, %%xmm2 \n\t"
                    "mulps %%xmm0, %%xmm3 \n\t":);
                asm("movups %%xmm1,%0"::"m"(FX(i)));
                asm("movups %%xmm2,%0"::"m"(FY(i)));
                asm("movups %%xmm3,%0"::"m"(FZ(i)));
        }
#endif            /*****************************/


#ifndef USE_SSE   /********[ C ONLY ]********/
        for (i=0; i<len; i++) {
                FX(i) += FRICTION*SX(i);
                FY(i) += FRICTION*SY(i);
                FZ(i) += FRICTION*SZ(i);
                for (j=i+1; j<len; j++) {
                        dX = X(j)-X(i);
                        dY = Y(j)-Y(i);
                        dZ = Z(j)-Z(i);
                        if (check_edge(i,j)) {
                                a = ATTRACT*dX;
                                FX(i) += a; FX(j) -= a;
                                a = ATTRACT*dY;
                                FY(i) += a; FY(j) -= a;
                                a = ATTRACT*dZ;
                                FZ(i) += a; FZ(j) -= a;
                        }

                        D = dX*dX+dY*dY+dZ*dZ;
                        DD = D*D;
                        if (DD < MIN_DIST) DD = MIN_DIST;


                        a = REPULS*dX/DD;
                        FX(i) -= a; FX(j) += a;
                        a = REPULS*dY/DD;
                        FY(i) -= a; FY(j) += a;
                        a = REPULS*dZ/DD;
                        FZ(i) -= a; FZ(j) += a;

                }
        }
#else             /********[ C + SSE ]********/
	for (i=0; i<len; i++) {

                asm("movss %0,%%xmm0\n\t"
                    "movss %1,%%xmm1\n\t"
                    "movss %2,%%xmm2\n\t"
                    "shufps $0, %%xmm0, %%xmm0 \n\t"
                    "shufps $0, %%xmm1, %%xmm1 \n\t"
                    "shufps $0, %%xmm2, %%xmm2 \n\t"
                    ::"m"(X(i)),"m"(Y(i)),"m"(Z(i)));

		for (j=i+1; j<len; j+=4) {

                        asm("movups %0, %%xmm3 \n\t"
                            "movups %1, %%xmm4 \n\t"
                            "movups %2, %%xmm5 \n\t"
                            "subps %%xmm0, %%xmm3 \n\t" // xmm3=dX
                            "subps %%xmm1, %%xmm4 \n\t" // xmm4=dY
                            "subps %%xmm2, %%xmm5 \n\t" // xmm5=dZ
                            ::"m"(X(j)),"m"(Y(j)),"m"(Z(j)));

                        attract[0] = ATTRACT*check_edge(i,j);
                        attract[1] = ATTRACT*check_edge(i,j+1);
                        attract[2] = ATTRACT*check_edge(i,j+2);
                        attract[3] = ATTRACT*check_edge(i,j+3);

                        LOG("attract %2i %2i: %5i %5i %5i %5i\n", i,j,attract[0],attract[1],attract[2],attract[3]);

			if (attract[0] || attract[1] || attract[2] || attract[3]) {
                                asm("movaps %0, %%xmm6 \n\t"
                                    "mulps %%xmm3, %%xmm6 \n\t"
                                    "movups %2, %%xmm7 \n\t"
                                    "movaps %%xmm6, %1 \n\t"
                                    "subps %%xmm6, %%xmm7 \n\t"
                                    "movups %%xmm7, %2 \n\t"::"m"(attract[0]), "m"(tmpsse1[0]), "m"(FX(j)));
                                LOG("attract X: %+.3f %+.3f %+.3f %+.3f\n",
                                       tmpsse1[0], tmpsse1[1], tmpsse1[2], tmpsse1[3]);

                                asm("movaps %0, %%xmm6 \n\t"
                                    "mulps %%xmm4, %%xmm6 \n\t"
                                    "movups %2, %%xmm7 \n\t"
                                    "movaps %%xmm6, %1 \n\t"
                                    "subps %%xmm6, %%xmm7 \n\t"
                                    "movups %%xmm7, %2 \n\t"::"m"(attract[0]), "m"(tmpsse2[0]), "m"(FY(j)));
                                LOG("attract Y: %+.3f %+.3f %+.3f %+.3f\n",
                                       tmpsse2[0], tmpsse2[1], tmpsse2[2], tmpsse2[3]);

                                asm("movaps %0, %%xmm6 \n\t"
                                    "mulps %%xmm5, %%xmm6 \n\t"
                                    "movups %2, %%xmm7 \n\t"
                                    "movaps %%xmm6, %1 \n\t"
                                    "subps %%xmm6, %%xmm7 \n\t"
                                    "movups %%xmm7, %2 \n\t"::"m"(attract[0]), "m"(tmpsse3[0]), "m"(FZ(j)));
                                LOG("attract Z: %+.3f %+.3f %+.3f %+.3f\n",
                                       tmpsse3[0], tmpsse3[1], tmpsse3[2], tmpsse3[3]);


                                if (attract[0]) { FX(i) += tmpsse1[0]; FY(i) += tmpsse2[0]; FZ(i) += tmpsse3[0];}
                                if (attract[1]) { FX(i) += tmpsse1[1]; FY(i) += tmpsse2[1]; FZ(i) += tmpsse3[1];}
                                if (attract[2]) { FX(i) += tmpsse1[2]; FY(i) += tmpsse2[2]; FZ(i) += tmpsse3[2];}
                                if (attract[3]) { FX(i) += tmpsse1[3]; FY(i) += tmpsse2[3]; FZ(i) += tmpsse3[3];}

			}


                        asm("movaps %%xmm3, %%xmm7 \n\t"
                            "movaps %%xmm4, %%xmm6 \n\t"
                            "mulps %%xmm3, %%xmm7 \n\t"
                            "mulps %%xmm4, %%xmm6 \n\t"
                            "addps %%xmm6, %%xmm7 \n\t"
                            "movaps %%xmm5, %%xmm6 \n\t"
                            "mulps %%xmm5, %%xmm6 \n\t"
                            "addps %%xmm6, %%xmm7 \n\t" // xmm7 = D = dX*dX+dY*dY+dZ*dZ
                            "mulps %%xmm7, %%xmm7 \n\t"
                            "maxps %0, %%xmm7 \n\t"     // xmm7 = max(MIN_DIST, D^2)
                            ::"m"(min_dist[0]));

                        asm("movaps %0, %%xmm6 \n\t"  // xmm6 = repuls
                            "divps %%xmm7, %%xmm3 \n\t"
                            "divps %%xmm7, %%xmm4 \n\t"
                            "divps %%xmm7, %%xmm5 \n\t"
                            "mulps %%xmm6, %%xmm3 \n\t"
                            "mulps %%xmm6, %%xmm4 \n\t"
                            "mulps %%xmm6, %%xmm5 \n\t" // xmm3,4,5 = dfx,dfy,dfz
                            :: "m"(repuls[0]));

                        asm("movaps %%xmm3, %0\n\t"
                            "movaps %%xmm4, %1\n\t"
                            "movaps %%xmm5, %2\n\t"
                            ::"m"(tmpsse1[0]),"m"(tmpsse2[0]),"m"(tmpsse3[0]));

                        asm("movups %0, %%xmm6 \n\t"
                            "movups %1, %%xmm7 \n\t"
                            "addps %%xmm3, %%xmm6 \n\t"
                            "addps %%xmm4, %%xmm7 \n\t"
                            "movups %2, %%xmm3 \n\t"
                            "movups %%xmm6, %0 \n\t"
                            "addps %%xmm5, %%xmm3 \n\t"
                            "movups %%xmm7, %1 \n\t"
                            "movups %%xmm3, %2 \n\t"
                            ::"m"(FX(j)), "m"(FY(j)), "m"(FZ(j)));

                        CONDADD(j,len,tmpsse1);
                        FX(i) -= tmpsse1[0];
                        CONDADD(j,len,tmpsse2);
                        FY(i) -= tmpsse2[0];
                        CONDADD(j,len,tmpsse3);
                        FZ(i) -= tmpsse3[0];
		}
	}
#endif            /***************************/
        dt *= ACCEL;


#ifndef USE_SSE   /********[ C ONLY ]********/
        dA = 0;
	for (i=0; i<CN*len; i++) {
                if (!F(i)) continue;
		a = F(i)*dt;
		S(i) += a;
		a = (S(i)+0.5*a)*dt;
		C(i) += a;
		dA += fabs(a);
        }
#else             /********[ C + SSE ]********/
        asm("movaps %0, %%xmm7 \n\t"    // xmm7 = dA = 0
            "movaps %1, %%xmm6 \n\t"    // xmm6 = 0.5
            "movss %2,%%xmm0 \n\t"
            "shufps $0, %%xmm0, %%xmm0 \n\t" // xmm1=(dt,dt,dt,dt)
                    ::"m"(zero[0]),"m"(half[0]), "m"(dt));

	for (i=0; i<len; i+=4) {

                asm("movups %0,%%xmm1 \n\t" // xmm1=FX
                    "movups %1,%%xmm2 \n\t" // xmm2=SX
                    "movups %2,%%xmm3 \n\t" // xmm3=X
                    "mulps %%xmm0, %%xmm1 \n\t" // xmm1=F*dt
                    "addps %%xmm1, %%xmm2 \n\t" // xmm2=S+dS=S+Fdt
                    "mulps %%xmm6, %%xmm1 \n\t"
                    "addps %%xmm2, %%xmm1 \n\t"
                    "mulps %%xmm0, %%xmm1 \n\t" // xmm1 = (S+0.5*F*dt)*dt = dX
                    "addps %%xmm1, %%xmm3 \n\t"
                    "movups %%xmm3, %2 \n\t"
                    "mulps %%xmm3,%%xmm3 \n\t"
                    "movups %%xmm2, %1 \n\t"
                    "addps %%xmm3, %%xmm7 \n\t" //xmm7 = dA += dX^2
                    ::"m"(FX(i)),"m"(SX(i)),"m"(X(i)));

                asm("movups %0,%%xmm1 \n\t" // xmm1=FY
                    "movups %1,%%xmm2 \n\t" // xmm2=SY
                    "movups %2,%%xmm3 \n\t" // xmm3=Y
                    "mulps %%xmm0, %%xmm1 \n\t" // xmm1=F*dt
                    "addps %%xmm1, %%xmm2 \n\t" // xmm2=S+dS=S+Fdt
                    "mulps %%xmm6, %%xmm1 \n\t"
                    "addps %%xmm2, %%xmm1 \n\t"
                    "mulps %%xmm0, %%xmm1 \n\t" // xmm1 = (S+0.5*F*dt)*dt = dY
                    "addps %%xmm1, %%xmm3 \n\t"
                    "movups %%xmm3, %2 \n\t"
                    "mulps %%xmm3,%%xmm3 \n\t"
                    "movups %%xmm2, %1 \n\t"
                    "addps %%xmm3, %%xmm7 \n\t" //xmm7 = dA += dX^2
                    ::"m"(FY(i)),"m"(SY(i)),"m"(Y(i)));

                asm("movups %0,%%xmm1 \n\t" // xmm1=FZ
                    "movups %1,%%xmm2 \n\t" // xmm2=SZ
                    "movups %2,%%xmm3 \n\t" // xmm3=Z
                    "mulps %%xmm0, %%xmm1 \n\t" // xmm1=F*dt
                    "addps %%xmm1, %%xmm2 \n\t" // xmm2=S+dS=S+Fdt
                    "mulps %%xmm6, %%xmm1 \n\t"
                    "addps %%xmm2, %%xmm1 \n\t"
                    "mulps %%xmm0, %%xmm1 \n\t" // xmm1 = (S+0.5*F*dt)*dt = dZ
                    "addps %%xmm1, %%xmm3 \n\t"
                    "movups %%xmm3, %2 \n\t"
                    "mulps %%xmm3,%%xmm3 \n\t"
                    "movups %%xmm2, %1 \n\t"
                    "addps %%xmm3, %%xmm7 \n\t" //xmm7 = dA += dX^2
                    ::"m"(FZ(i)),"m"(SZ(i)),"m"(Z(i)));

                }
        asm("movaps %%xmm7, %0"::"m"(tmpsse1[0]));
        dA = tmpsse1[0]+tmpsse1[1]+tmpsse1[2]+tmpsse1[3];

        for (i=0; i<len; i++) {
            PX(i) = X(i);
            PY(i) = Y(i);
            PZ(i) = Z(i);
        }
#endif            /***************************/


	return dA/(len+0.1);
}

"""

        if mode == 3:
            sse_code = "#define USE_SSE\r\n" + sse_code

        physics_engine = PyInline.build(language="C", code=sse_code)
        physics_engine.C_ENGINE = 1
    else:
        physics_engine = python_physics_engine
    return physics_engine


class Edge(cylinder):
    def __init__(self, o1, o2, *args, **kargs):
        param = {"radius": 0.2, "color": (0.7, 0.7, 1)}
        param.update(kargs)
        self.o1 = o1
        self.o2 = o2
        cylinder.__init__(self, *args, **param)
        self.update()
        self.pickable = 0

    def update(self):
        self.pos = self.o1.pos
        self.axis = self.o2.pos - self.o1.pos


def randvect():
    return vector(random.random(), random.random(), random.random())


def randcol():
    v = randvect()
    s = v[0] + v[1] + v[2]
    if s < 1:
        v *= 1 / (0.001 + s)
    return v


class Node(sphere):
    def __init__(self, node_id, *args, **kargs):
        self.param = {"radius": 1, "pos": randvect(), "color": randcol()}
        self.param.update(kargs)
        self.id = node_id
        self.edges = {}
        self.pickable = 1
        self.PV = vector()
        self.V = vector()

        sphere.__init__(self, *args, **self.param)

        self.label = label(
            text=node_id,
            pos=self.pos,
            space=self.radius,
            xoffset=10,
            yoffset=20,
            visible=0,
        )
        self.update_label()

    def update_label(self):
        text = [self.id]
        for k, v in self.param.items():
            if k in ["radius", "pos", "color"]:
                setattr(self, k, v)
            else:
                text.append("%s = %s" % (k, v))
        self.label.text = str("\n".join(text))

    def update_param(self, **kargs):
        self.param.update(kargs)
        self.update_label()

    def action(self):
        self.label.pos = self.pos
        self.label.visible ^= 1

    def update(self, dt):
        self.label.pos = self.pos

    def get_state(self):
        for k in self.param:
            if hasattr(self, k):
                self.param[k] = getattr(self, k)
        return self.param

    def dump(self):
        return repr(
            (self.id, self.get_state(), [x.id for x in list(self.edges.keys())])
        )

    @classmethod
    def from_string(cls, s):
        l = eval(s)
        node_id, state, edges = l[:3]
        o = cls(node_id, **state)
        o._tmp_edges = edges
        return o


povexport.legal[Node] = povexport.legal[sphere]
povexport.legal[Edge] = povexport.legal[cylinder]


class World:
    def __init__(self, physics_engine, friction=-0.5, attraction=1, repulsion=256):
        self.physics_engine = physics_engine
        self.friction = friction
        self.attraction = attraction
        self.repulsion = repulsion
        self.reset_world()

    def reset_world(self):
        self.world = {}
        self.lst = []
        self.world_len = 0
        self.edges = []
        self.coords = []
        self.speeds = []
        self.cinematic_change = 1

    def register(self, o):
        self.world[o.id] = o
        self.lst.append(o)
        o.num = self.world_len
        self.coords.append(o.pos.astuple())
        self.speeds.append((0.0, 0.0, 0.0))
        self.world_len += 1

    def add_edge(self, o1, o2):
        self.edges.append(Edge(o1, o2))
        self.physics_engine.add_edge(o1.num, o2.num)

    def __getitem__(self, item):
        return self.world[item]

    def __contains__(self, item):
        return item in self.world

    def get(self, *args):
        return self.world.get(*args)

    def dump_to_file(self, f):
        for o in self.lst:
            f.write(o.dump())
            f.write("\n")
        f.close()

    def load_from_file(self, f):
        while 1:
            l = f.readline()
            if not l:
                break
            o = Node.from_string(l)
            self.register(o)
        for o in self.lst:
            if hasattr(o, "_tmp_edges"):
                for e in o._tmp_edges:
                    if e not in self.world:
                        print("%s: edge to [%s] not found" % (o.id, e), file=sys.stderr)
                        continue
                    o2 = self.world[e]
                    o.edges[o2] = None
                    if o in o2.edges:
                        self.add_edge(o, o2)
                del o._tmp_edges

    def update_edges(self):
        for e in self.edges:
            e.update()

    def update(self, dt):
        self.physics_engine.update(
            self,
            self.coords,
            self.speeds,
            self.cinematic_change,
            dt,
            self.attraction,
            self.repulsion,
        )
        self.cinematic_change = 0
        if self.physics_engine.C_ENGINE:
            for i in range(self.world_len):
                self.lst[i].pos = self.coords[i]
                self.lst[i].update(dt)
        else:
            for i in range(self.world_len):
                self.lst[i].update(dt)
        self.update_edges()


def mkcol():
    def norm(x, y, z):
        if x + y + z < 1:
            t = 1 - max(x, y, z)
            x, y, z = x + t, y + t, z + t
        return x, y, z

    return norm(random.random(), random.random(), random.random())


def ip2num(ip):
    a, b, c, d = struct.unpack("!lLlL", socket.inet_pton(socket.AF_INET6, ip))
    return (a << 32 | b), (c << 32 | d)


class GlowingService:
    def __init__(self):
        self.lst = {}
        self.run = 1
        _thread.start_new_thread(self.glowing_thread, ())

    def __del__(self):
        self.run = 0

    def glow_node(self, node):
        if node not in self.lst:
            self.lst[node] = (node.radius, node.color)

    def unglow_node(self, node):
        if node in self.lst:
            node.radius, node.color = self.lst.pop(node)

    def toggle_glow(self, node):
        if node in self.lst:
            self.unglow_node(node)
        else:
            self.glow_node(node)

    def glowing_thread(self):
        t = 0
        while self.run:
            rate(25)
            mult = 1.1 + 0.3 * cos(t * 2 * pi / 25)
            for n, v in self.lst.items():
                rad, col = v
                n.radius = rad * mult
                n.red = min(1, col[0] * mult)
                n.green = min(1, col[1] * mult)
                n.blue = min(1, col[2] * mult)
            t += 1

    def __iter__(self):
        return iter(self.lst)


class RotateService:
    def __init__(self, scene, angle=pi / 300):
        self.lock = _thread.allocate_lock()
        self.lock.acquire()
        self.scene = scene
        self.angle = angle
        _thread.start_new_thread(self.rotate_thread, ())

    def rotate(self):
        if self.lock.locked():
            self.lock.release()

    def stop_rotate(self):
        self.lock.acquire(0)

    def set_angle(self, angle):
        self.angle = angle

    def rotate_thread(self):
        t = 0.0
        while 1:
            rate(50)
            if self.lock.locked():
                self.lock.acquire()
                self.lock.release()
            self.scene.forward = (cos(t), 0, sin(t))
            t += self.angle


class RTGraphService(dbus.service.Object):
    def __init__(
        self,
        bus,
        dbpath,
        physics_engine,
        input=[sys.stdin],
        startfile=None,
        savefile=None,
        stereo=None,
    ):
        dbus.service.Object.__init__(self, bus, dbpath)
        self.scene = display()
        self.scene.title = "RealTime Graph 3D"
        self.scene.exit = 0
        self.scene.ambient = 0.3
        if stereo is not None:
            self.scene.stereo = stereo
            self.scene.stereodepth = 2
        #        self.scene.width=100
        #        self.scene.height=50
        self.scene.visible = 1
        self.cinematic_lock = _thread.allocate_lock()

        self.glow = GlowingService()
        self.rotate_service = RotateService(self.scene)

        self.the_world = World(physics_engine)
        self.the_world.scene = self.scene
        if startfile is not None:
            self.the_world.load_from_file(open(startfile))
        if savefile is not None:
            atexit.register(self.the_world.dump_to_file, open(savefile, "w"))

    @dbus.service.signal("org.secdev.rtgraph3d.events", signature="s")
    def node_click(self, message):
        pass

    @dbus.service.signal("org.secdev.rtgraph3d.events", signature="s")
    def node_shift_click(self, message):
        pass

    @dbus.service.signal("org.secdev.rtgraph3d.events", signature="s")
    def node_ctrl_click(self, message):
        pass

    @dbus.service.method(
        "org.secdev.rtgraph3d.command", in_signature="s", out_signature=""
    )
    def file_dump(self, fname):
        self.cinematic_lock.acquire()
        self.the_world.dump_to_file(open(fname, "w"))
        self.cinematic_lock.release()
        log.info("Dumped world to [%s]" % fname)

    @dbus.service.method(
        "org.secdev.rtgraph3d.command", in_signature="s", out_signature=""
    )
    def file_load(self, fname):
        self.cinematic_lock.acquire()
        self.the_world.load_from_file(open(fname))
        self.cinematic_lock.release()
        log.info("Loaded world from [%s]" % fname)

    @dbus.service.method(
        "org.secdev.rtgraph3d.command", in_signature="", out_signature="s"
    )
    def get_dump(self):
        return "not implemented..."

    @dbus.service.method(
        "org.secdev.rtgraph3d.command", in_signature="", out_signature="s"
    )
    def get_dot(self):
        s = 'graph "rtgraph" { \n'

        for e in self.the_world.edges:
            s += '\t "%s" -- "%s";\n' % (e.o1.id, e.o2.id)
        s += "}\n"
        return s

    @dbus.service.method(
        "org.secdev.rtgraph3d.command", in_signature="", out_signature=""
    )
    def reset_world(self):
        self.cinematic_lock.acquire()
        self.the_world.reset_world()
        for o in self.scene.objects:
            o.visible = 0
        self.cinematic_lock.release()
        log.info("Reseted world")

    @dbus.service.method(
        "org.secdev.rtgraph3d.command", in_signature="d", out_signature=""
    )
    def set_attraction(self, attract):
        self.the_world.attraction = attract

    @dbus.service.method(
        "org.secdev.rtgraph3d.command", in_signature="d", out_signature=""
    )
    def set_repulsion(self, repuls):
        self.the_world.repulsion = repuls

    @dbus.service.method(
        "org.secdev.rtgraph3d.command", in_signature="d", out_signature=""
    )
    def set_ambient(self, ambient):
        self.scene.ambient = ambient

    @dbus.service.method(
        "org.secdev.rtgraph3d.command", in_signature="d", out_signature=""
    )
    def auto_rotate_scene(self, angle):
        if angle:
            self.rotate_service.set_angle(angle)
        self.rotate_service.rotate()

    @dbus.service.method(
        "org.secdev.rtgraph3d.command", in_signature="", out_signature=""
    )
    def stop_auto_rotate_scene(self):
        self.rotate_service.stop_rotate()

    @dbus.service.method(
        "org.secdev.rtgraph3d.command", in_signature="s", out_signature="s"
    )
    def execute(self, cmd):
        log.info("--- Begin exec [%s]" % cmd)
        res = eval(cmd)
        log.info(res)
        log.info("--- End exec [%s]" % cmd)
        return "%s" % res

    @dbus.service.method(
        "org.secdev.rtgraph3d.command", in_signature="", out_signature=""
    )
    def check(self):
        for o in self.the_world.lst:
            for o2 in o.edges:
                if o not in o2.edges:
                    log.error("%s ==> %s \t %s ==> %s" % (o.id, o2.id, id(o), id(o2)))
            log.info(
                "Checked %i nodes, %i edges."
                % (len(self.the_world.lst), len(self.the_world.edges))
            )

    @dbus.service.method(
        "org.secdev.rtgraph3d.command", in_signature="sa{sv}sa{sv}", out_signature=""
    )
    def new_edge(self, id1, attr1, id2, attr2):
        id1 = str(id1)
        id2 = str(id2)
        attr1 = dict([(str(a), b.__class__.__base__(b)) for a, b in attr1.items()])
        attr2 = dict([(str(a), b.__class__.__base__(b)) for a, b in attr2.items()])

        if id1 == id2:
            raise Exception("Nodes are identical")

        n1 = self.the_world.get(id1)
        n2 = self.the_world.get(id2)
        if n1 is None and n2 is not None:
            n2, n1 = n1, n2
            id1, id2 = id2, id1
            attr1, attr2 = attr2, attr1

        if n1 is None:
            n1 = Node(id1, **attr1)
            self.the_world.register(n1)
        if n2 is None:
            if "pos" not in attr2:
                attr2["pos"] = n1.pos + randvect()
            n2 = Node(id2, **attr2)
            self.the_world.register(n2)

        if n1 in n2.edges:
            raise Exception("Edge %s-%s alread exists" % (id1, id2))

        n1.edges[n2] = None
        n2.edges[n1] = None
        self.the_world.add_edge(n1, n2)
        self.the_world.cinematic_change = 1

        log.info("Ok for [%s]-[%s]" % (id1, id2))

    @dbus.service.method(
        "org.secdev.rtgraph3d.command", in_signature="sa{sv}", out_signature=""
    )
    def update_node(self, node_id, attr):
        attr = dict([(str(a), b.__class__.__base__(b)) for a, b in attr.items()])
        node = self.the_world.get(node_id)
        node.update_param(**attr)

    @dbus.service.method(
        "org.secdev.rtgraph3d.command", in_signature="s", out_signature=""
    )
    def toggle(self, node_id):
        self.the_world[str(node_id)].action()

    @dbus.service.method(
        "org.secdev.rtgraph3d.command", in_signature="s", out_signature=""
    )
    def glow(self, node_id):
        self.glow.glow_node(self.the_world[str(node_id)])

    @dbus.service.method(
        "org.secdev.rtgraph3d.command", in_signature="s", out_signature=""
    )
    def unglow(self, node_id):
        self.glow.unglow_node(self.the_world[str(node_id)])

    @dbus.service.method(
        "org.secdev.rtgraph3d.command", in_signature="", out_signature=""
    )
    def unglow_all(self):
        for n in self.the_world.lst:
            self.glow.unglow_node(n)

    @dbus.service.method(
        "org.secdev.rtgraph3d.command", in_signature="ss", out_signature="as"
    )
    def find(self, attr, val):
        res = []
        rval = re.compile(str(val))
        attr = str(attr)
        for n in self.the_world.lst:
            if attr in n.param:
                v = n.param[attr]
                if type(v) is not str:
                    v = repr(v)
                if rval.search(v):
                    res.append(n.id)
        return res

    @dbus.service.method(
        "org.secdev.rtgraph3d.command", in_signature="", out_signature="as"
    )
    def get_all_nodes(self):
        return [n.id for n in self.the_world.lst]


def cinematic_thread(svc, POVdump=None, ACCEL=ACCEL, DT=DT):
    log.info("Cinematic thread started")
    the_world = svc.the_world
    scene = the_world.scene
    picked = None
    frames = -1
    while 1:
        frames += 1
        rate(ACCEL / DT)
        svc.cinematic_lock.acquire()
        try:
            if scene.kb.keys:
                k = scene.kb.getkey()
                if k == "Q":
                    # send event
                    return
            if scene.mouse.events:
                ev = scene.mouse.getevent()
                if ev.release == "left":
                    if picked:
                        the_world.speeds[picked.num] = (
                            (scene.mouse.pos - picked.PV) / DT
                        ).astuple()
                        the_world.cinematic_change = 1
                        picked = None
                    else:
                        o = ev.pick
                        if ev.shift and o:
                            if hasattr(o, "id"):
                                svc.node_shift_click(o.id)
                        elif ev.ctrl and o:
                            if hasattr(o, "id"):
                                svc.node_ctrl_click(o.id)
                        else:
                            if hasattr(o, "action"):
                                o.action()
                if ev.drag == "left":
                    if ev.pick and ev.pick.pickable:
                        picked = ev.pick

            if picked:
                picked.PV = picked.pos
                picked.pos = scene.mouse.pos
                picked.V = vector()
                the_world.coords[picked.num] = picked.pos.astuple()
                the_world.speeds[picked.num] = (0.0, 0.0, 0.0)
                the_world.cinematic_change = 1

            the_world.update(DT)
            the_world.update_edges()
            if POVdump is not None:
                fname = POVdump % frames
                povexport.export(
                    filename=fname, display=scene, include_list=["colors.inc"]
                )

        except:
            log.exception(
                "FRAME=%i: Catched exception in the cinematic thread!" % frames
            )

        svc.cinematic_lock.release()


def usage():
    print(
        """rtgraph3D [-w savefile] [-r startfile] [-m <mode>]
    -P <fname_tmpl> export to POV, filename template (ex: /tmp/foo/bar-%i.pov)
    -d
    -c {s|d}        choose between static and dynamic mode
    -m {p|c|s}      Python (slow), C (quick) and SSE (quickest) physics engine
    -w <savefile>   save world in this file
    -r <startfile>  read world from this file
    -s <stereo>     stereo mode (active, passive, crosseyed, redcyan, redblue, yellowblue)""",
        file=sys.stderr,
    )
    sys.exit(0)


class Cinematic:
    static = 0
    dynamic = 1


if __name__ == "__main__":
    INPUT = [sys.stdin]
    STARTFILE = None
    SAVEFILE = None
    STEREO = None
    CINEMATIC = Cinematic.dynamic
    POVDUMP = None
    MODE = 0
    try:
        opts = getopt.getopt(sys.argv[1:], "htr:w:s:c:P:m:")

        for opt, optarg in opts[0]:
            if opt == "-h":
                usage()
            elif opt == "-t":
                MODE = socket.SOCK_STREAM
            elif opt == "-r":
                STARTFILE = optarg
            elif opt == "-s":
                STEREO = optarg
            elif opt == "-w":
                SAVEFILE = optarg
            elif opt == "-m":
                try:
                    MODE = {"p": 1, "c": 2, "s": 3}[optarg.lower()]
                except KeyError:
                    raise getopt.GetoptError("unkonwn mode [%s]" % optarg)
            elif opt == "-P":
                POVDUMP = optarg
            elif opt == "-c":
                if optarg.startswith("s"):  # static
                    CINEMATIC = Cinematic.static
                elif optarg.startswith("d"):  # dynamic
                    CINEMATIC = Cinematic.dynamic
    except getopt.GetoptError as msg:
        log.exception(msg)
        sys.exit(-1)

    gobject.threads_init()
    dbus.glib.init_threads()
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SessionBus()
    name = dbus.service.BusName("org.secdev.rtgraph3d", bus)
    svc = RTGraphService(
        bus,
        "/control",
        get_physics_engine(MODE),
        INPUT,
        startfile=STARTFILE,
        savefile=SAVEFILE,
        stereo=STEREO,
    )

    if CINEMATIC == Cinematic.dynamic:
        _thread.start_new_thread(
            cinematic_thread,
            (
                svc,
                POVDUMP,
            ),
        )

    mainloop = gobject.MainLoop()
    log.info("Entering main loop")
    mainloop.run()
