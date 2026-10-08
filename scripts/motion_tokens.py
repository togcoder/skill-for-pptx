#!/usr/bin/env python3
"""Motion tokens from open design systems, translated to PowerPoint (T029).

PowerPoint timing has no cubic-bezier easing: a behaviour only has
``accel``/``decel`` fractions (SMIL: speed ramps up linearly over the first
fraction, holds, ramps down over the last). The easing curves of IBM Carbon
(@carbon/motion, Apache-2.0) and Material Design 3 (@material/web tokens,
Apache-2.0) are fitted to the closest accel/decel pair, so a recipe can ask for
"emphasized-decelerate" and get PowerPoint's best equivalent.

    motion_tokens.py        # print every token with its fit and error
"""
import json
import sys

# name -> cubic-bezier(x1, y1, x2, y2), source
EASINGS={
    "carbon-standard-productive":((0.2,0,0.38,0.9),"Carbon"),
    "carbon-standard-expressive":((0.4,0.14,0.3,1),"Carbon"),
    "carbon-entrance-productive":((0,0,0.38,0.9),"Carbon"),
    "carbon-entrance-expressive":((0,0,0.3,1),"Carbon"),
    "carbon-exit-productive":((0.2,0,1,0.9),"Carbon"),
    "carbon-exit-expressive":((0.4,0.14,1,1),"Carbon"),
    "md-emphasized":((0.2,0,0,1),"Material 3"),
    "md-emphasized-decelerate":((0.05,0.7,0.1,1),"Material 3"),
    "md-emphasized-accelerate":((0.3,0,0.8,0.15),"Material 3"),
    "md-standard":((0.2,0,0,1),"Material 3"),
    "md-standard-decelerate":((0,0,0,1),"Material 3"),
    "md-standard-accelerate":((0.3,0,1,1),"Material 3"),
    "md-legacy":((0.4,0,0.2,1),"Material 3"),
}
# Role names the tools use -> token.
# Single accel/decel pairs reproduce Carbon's curves within 1.5-8% of progress,
# but Material's emphasized curves only within 18-44% (their fast start needs
# several keyframes). Roles therefore map to Carbon; md-* stay addressable.
ROLES={"standard":"carbon-standard-productive","expressive":"carbon-standard-expressive",
       "enter":"carbon-entrance-productive","enter-expressive":"carbon-entrance-expressive",
       "exit":"carbon-exit-productive","exit-expressive":"carbon-exit-expressive"}
# Durations in ms. Carbon: fast-01..slow-02. Material 3: short1..extra-long4.
DURATIONS={"carbon":{"fast-01":70,"fast-02":110,"moderate-01":150,"moderate-02":240,"slow-01":400,"slow-02":700},
           "md":{"short1":50,"short2":100,"short3":150,"short4":200,"medium1":250,"medium2":300,"medium3":350,
                 "medium4":400,"long1":450,"long2":500,"long3":550,"long4":600,"extra-long1":700,
                 "extra-long2":800,"extra-long3":900,"extra-long4":1000}}


def bezier_progress(curve,t):
    """y at x=t for a CSS cubic-bezier (bisection on the monotonic x(s))."""
    x1,y1,x2,y2=curve

    def b(a1,a2,s):
        u=1-s
        return 3*u*u*s*a1+3*u*s*s*a2+s**3
    lo,hi=0.0,1.0
    for _ in range(40):
        mid=(lo+hi)/2
        if b(x1,x2,mid)<t:
            lo=mid
        else:
            hi=mid
    return b(y1,y2,(lo+hi)/2)


def ppt_progress(t,accel,decel):
    """Progress of a PowerPoint behaviour with accel/decel fractions."""
    if accel+decel<=0:
        return t
    v=1/(1-accel/2-decel/2)
    if t<accel:
        return v*t*t/(2*accel)
    if t<=1-decel:
        return v*(accel/2+(t-accel))
    return 1-v*(1-t)**2/(2*decel)


def fit(curve,step=0.05,samples=101):
    """(accel, decel, max_error) minimising the worst progress gap."""
    target=[bezier_progress(curve,i/(samples-1)) for i in range(samples)]
    best=(0.0,0.0,9.0)
    n=round(1/step)
    for i in range(n+1):
        for j in range(n+1-i):
            a,d=i*step,j*step
            err=max(abs(ppt_progress(k/(samples-1),a,d)-target[k]) for k in range(samples))
            if err<best[2]:
                best=(round(a,2),round(d,2),round(err,3))
    return best


_FITS={}


def ease(name):
    """(accel, decel) for a role ("enter", "exit", "emphasized", ...) or a token name."""
    token=ROLES.get(name,name)
    if token not in _FITS:
        _FITS[token]=fit(EASINGS[token][0])
    return _FITS[token][:2]


def travel_ms(distance,base=350,per_slide=650,low=300,high=1200):
    """Duration for a move of ``distance`` (fraction of the slide diagonal).
    Longer journeys take longer, as Material 3 and Carbon recommend.
    ponytail: linear in distance; presentation timing is slower than UI timing,
    so this sits in Material's medium..extra-long band."""
    return int(max(low,min(high,base+per_slide*distance)))


def main():
    rows={name:{"bezier":c,"source":src,**dict(zip(("accel","decel","max_error"),fit(c)))}
          for name,(c,src) in EASINGS.items()}
    json.dump({"roles":ROLES,"easings":rows,"durations_ms":DURATIONS},sys.stdout,indent=1)
    print()


if __name__=="__main__":
    main()
