/* -------------------------------------------------------------------------- */
/* GraphBLAS/Demo/simple_timer.c: a timer for performance measurements        */
/* -------------------------------------------------------------------------- */

/* SuiteSparse:GraphBLAS, Timothy A. Davis, (c) 2017, All Rights Reserved.    */
/* http://suitesparse.com   See GraphBLAS/Doc/License.txt for license.        */

/* -------------------------------------------------------------------------- */

/* simple_timer:  a portable timer for accurate performance measurements */

#include "simple_timer.h"

#include <sys/time.h>

/* -------------------------------------------------------------------------- */
/* simple_tic: return the current wallclock time in high resolution           */
/* -------------------------------------------------------------------------- */

void simple_tic         /* returns current time in seconds and nanoseconds */
(
    double tic [2]      /* tic [0]: seconds, tic [1]: nanoseconds */
)
{

    #if defined ( _OPENMP )

        /* OpenMP is available; use the OpenMP timer function */
        tic [0] = omp_get_wtime ( ) ;
        tic [1] = 0 ;

    #elif defined ( __linux__ )

        /* Linux has a very low resolution clock() function, so use the high
           resolution clock_gettime instead.  May require -lrt */
        struct timespec t ;
        clock_gettime (CLOCK_MONOTONIC, &t) ;
        tic [0] = (double) t.tv_sec ;
        tic [1] = (double) t.tv_nsec ;

    #else

        /* The ANSI C11 clock() function is used instead.  This gives the
           processor time, not the wallclock time, and it might have low
           resolution.  It returns the time since some unspecified fixed time
           in the past, as a clock_t integer.  The clock ticks per second are
           given by CLOCKS_PER_SEC.  In Mac OSX this is a very high resolution
           clock, and clock ( ) is faster than clock_get_time (...) ; */
        clock_t t = clock ( ) ;
        tic [0] = ((double) t) / ((double) CLOCKS_PER_SEC) ;
        tic [1] = 0 ;

    #endif

}

/* -------------------------------------------------------------------------- */
/* simple_toc: return the time since the last simple_tic                      */
/* -------------------------------------------------------------------------- */

double simple_toc           /* returns time since last simple_tic */
(
    const double tic [2]    /* tic from last call to simple_tic */
)
{
    double toc [2] ;
    simple_tic (toc) ;
    return ((toc [0] - tic [0]) + 1e-9 * (toc [1] - tic [1])) ;
}

uint64_t get_unix_timestamp_milliseconds() {
	struct timeval tv = {};

	gettimeofday(&tv, NULL);

	const uint64_t milliseconds_since_epoch =
		(uint64_t)(tv.tv_sec) * 1000 +
		(uint64_t)(tv.tv_usec) / 1000;

	return milliseconds_since_epoch;
}
