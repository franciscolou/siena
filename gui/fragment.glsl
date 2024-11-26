uniform vec4 planecolor;
uniform vec4 clipplane[1];

void main(void)
{
vec3 normal = normalize(gl_FrontFacing? f.normal : vec3(clipplane[0]));
vec3 light=normalize(f.light);
vec3 view=normalize(f.view);
float ndotl=dot(normal,light);
if (gl_FrontFacing)
    color=(mamb*lamb+mdif*ldif*max(0,ndotl))*texture(decal,f.texcoord);
else
    color=(planecolor*lamb+planecolor*ldif*max(0,ndotl));
if(ndotl>0){
vec3 refl=normalize(reflect(-light,normal));
color+=mspe*lspe*pow(max(0,dot(refl,view)),mshi);
}
}